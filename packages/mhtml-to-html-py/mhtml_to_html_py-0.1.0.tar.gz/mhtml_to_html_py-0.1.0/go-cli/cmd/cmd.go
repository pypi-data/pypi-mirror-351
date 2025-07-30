package cmd

import (
	"bufio"
	"bytes"
	"errors"
	"fmt"
	"io"
	"log"
	"mime"
	"net/textproto"
	"os"
	"path"
	"path/filepath"
	"strings"
	"unicode"

	"github.com/PuerkitoBio/goquery"
	"github.com/alecthomas/kong"
)

type options struct {
	Verbose bool     `help:"Verbose printing."`
	About   bool     `help:"Show about."`
	Output  string   `short:"o" help:"Output file (default: stdout)."`
	MHTML   []string `arg:"" optional:"" help:"Input MHTML files (*.mht, *.mhtml)."`
}

type MHTMLToHTML struct {
	options
}

func (h *MHTMLToHTML) Run() (err error) {
	kong.Parse(h,
		kong.Name("mhtml-to-html"),
		kong.Description("Convert MHTML files to HTML (outputs to stdout by default)."),
		kong.UsageOnError(),
	)
	if h.About {
		fmt.Println("Visit https://github.com/gonejack/mhtml-to-html")
		return
	}
	if len(h.MHTML) == 0 {
		for _, pattern := range []string{"*.mht", "*.mhtml"} {
			found, _ := filepath.Glob(pattern)
			h.MHTML = append(h.MHTML, found...)
		}
	}
	if len(h.MHTML) == 0 {
		fmt.Fprintf(os.Stderr, "Usage: %s [options] <input.mht|input.mhtml>\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "\nExamples:\n")
		fmt.Fprintf(os.Stderr, "  %s file.mht                    # Output HTML to stdout\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  %s file.mht -o output.html     # Save HTML to file\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "  %s --help                      # Show all options\n", os.Args[0])
		return errors.New("no input files specified")
	}
	if h.Output == "" && len(h.MHTML) > 1 {
		return errors.New("cannot output multiple files to stdout (use -o to specify output file)")
	}
	for _, mht := range h.MHTML {
		if h.Verbose {
			log.Printf("processing %s", mht)
		}
		if e := h.process(mht); e != nil {
			return fmt.Errorf("parse %s failed: %s", mht, e)
		}
	}
	return
}
func (h *MHTMLToHTML) process(mht string) error {
	fd, err := os.Open(mht)
	if err != nil {
		return err
	}
	defer fd.Close()
	tp := textproto.NewReader(bufio.NewReader(&trimReader{rd: fd}))
	hdr, err := tp.ReadMIMEHeader()
	if err != nil {
		return err
	}
	parts, err := parseMIMEParts(hdr, tp.R)
	if err != nil {
		return err
	}
	var html *part
	var saves = make(map[string]string)
	
	// If outputting to stdout, only extract HTML content, skip assets
	if h.Output == "" {
		for _, part := range parts {
			contentType := part.header.Get("Content-Type")
			if contentType == "" {
				continue
			}
			mimetype, _, err := mime.ParseMediaType(contentType)
			if err != nil {
				continue
			}
			if html == nil && mimetype == "text/html" {
				html = part
				break
			}
		}
	} else {
		// When saving to file, extract assets as before
		var savedir = strings.TrimSuffix(mht, filepath.Ext(mht)) + "_files"
		for idx, part := range parts {
			contentType := part.header.Get("Content-Type")
			if contentType == "" {
				return ErrMissingContentType
			}
			mimetype, _, err := mime.ParseMediaType(contentType)
			if err != nil {
				return err
			}
			if html == nil && mimetype == "text/html" {
				html = part
				continue
			}

			ext := ".dat"
			switch mimetype {
			case mime.TypeByExtension(".jpg"):
				ext = ".jpg"
			default:
				exts, err := mime.ExtensionsByType(mimetype)
				if err != nil {
					return err
				}
				if len(exts) > 0 {
					ext = exts[0]
				}
			}

			dir := path.Join(savedir, mimetype)
			err = os.MkdirAll(dir, 0766)
			if err != nil {
				return fmt.Errorf("cannot create dir %s: %s", dir, err)
			}
			file := path.Join(dir, fmt.Sprintf("%d%s", idx, ext))
			err = os.WriteFile(file, part.body, 0766)
			if err != nil {
				return fmt.Errorf("cannot write file%s: %s", file, err)
			}
			ref := part.header.Get("Content-Location")
			saves[ref] = file
		}
	}
	if html == nil {
		return errors.New("html not found")
	}

	// Apply encoding detection and conversion to HTML content
	convertedHTML, err := detectAndConvertEncoding(html.body, h.Verbose)
	if err != nil {
		if h.Verbose {
			log.Printf("Encoding conversion failed: %v, using original content", err)
		}
		convertedHTML = html.body
	}

	doc, err := goquery.NewDocumentFromReader(bytes.NewReader(convertedHTML))
	if err != nil {
		return err
	}
	
	// Only update references when saving to file (not stdout)
	if h.Output != "" {
		doc.Find("img,link,script").Each(func(i int, e *goquery.Selection) {
			h.changeRef(e, saves)
		})
	}
	txt, err := doc.Html()
	if err != nil {
		return err
	}
	
	if h.Output == "" {
		fmt.Print(txt)
		return nil
	}
	
	return os.WriteFile(h.Output, []byte(txt), 0766)
}
func (h *MHTMLToHTML) changeRef(e *goquery.Selection, saves map[string]string) {
	attr := "src"
	switch e.Get(0).Data {
	case "img":
		e.RemoveAttr("loading")
		e.RemoveAttr("srcset")
	case "link":
		attr = "href"
	}
	ref, _ := e.Attr(attr)
	local, exist := saves[ref]
	if exist {
		e.SetAttr(attr, local)
	}
}

type part struct {
	header textproto.MIMEHeader
	body   []byte
}
type trimReader struct {
	rd      io.Reader
	trimmed bool
}

func (tr *trimReader) Read(buf []byte) (int, error) {
	n, err := tr.rd.Read(buf)
	if err != nil {
		return n, err
	}
	if !tr.trimmed {
		t := bytes.TrimLeftFunc(buf[:n], tr.isSpace)
		tr.trimmed = true
		n = copy(buf, t)
	}
	return n, err
}
func (tr *trimReader) isSpace(r rune) bool {
	const (
		ZWSP   = '\u200B' // ZWSP represents zero-width space.
		ZWNBSP = '\uFEFF' // ZWNBSP represents zero-width no-break space.
		ZWJ    = '\u200D' // ZWJ represents zero-width joiner.
		ZWNJ   = '\u200C' // ZWNJ represents zero-width non-joiner.
	)
	switch r {
	case ZWSP, ZWNBSP, ZWJ, ZWNJ:
		return true
	default:
		return unicode.IsSpace(r)
	}
}
