package cmd

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"regexp"
	"strings"

	"golang.org/x/text/encoding"
	"golang.org/x/text/encoding/charmap"
	"golang.org/x/text/encoding/japanese"
	"golang.org/x/text/encoding/korean"
	"golang.org/x/text/encoding/simplifiedchinese"
	"golang.org/x/text/encoding/traditionalchinese"
	"golang.org/x/text/encoding/unicode"
)

// detectAndConvertEncoding detects the charset and converts content to UTF-8
func detectAndConvertEncoding(data []byte, verbose bool) ([]byte, error) {
	// First, try to detect charset from HTML meta tags
	detectedCharset := detectCharsetFromHTML(data)
	if verbose && detectedCharset != "" {
		log.Printf("Detected charset from HTML meta: %s", detectedCharset)
	}
	
	// If no charset found in meta tags, try simple heuristics
	if detectedCharset == "" {
		detectedCharset = detectCharsetByHeuristics(data, verbose)
	}
	
	// If still no charset detected, assume UTF-8
	if detectedCharset == "" {
		if verbose {
			log.Printf("No charset detected, assuming UTF-8")
		}
		return data, nil
	}
	
	// Normalize charset name
	detectedCharset = normalizeCharsetName(detectedCharset)
	
	// Convert to UTF-8 if not already UTF-8
	if !isUTF8Charset(detectedCharset) {
		converted, err := convertToUTF8(data, detectedCharset)
		if err != nil {
			if verbose {
				log.Printf("Failed to convert from %s to UTF-8: %v, using original data", detectedCharset, err)
			}
			return data, nil // Return original data on conversion failure
		}
		if verbose {
			log.Printf("Successfully converted from %s to UTF-8", detectedCharset)
		}
		return converted, nil
	}
	
	return data, nil
}

// detectCharsetFromHTML extracts charset from HTML meta tags
func detectCharsetFromHTML(data []byte) string {
	// Convert to string for regex matching (first 2KB should be enough for meta tags)
	searchData := data
	if len(data) > 2048 {
		searchData = data[:2048]
	}
	
	htmlContent := string(searchData)
	
	// Manual regex patterns for common meta tag formats
	patterns := []string{
		`<meta[^>]+charset\s*=\s*["\']?([^"\'\s>]+)`,
		`<meta[^>]+content\s*=\s*["\']?[^"\']*charset\s*=\s*([^"\'\s;>]+)`,
		`charset\s*=\s*([^"\'\s;>]+)`,
	}
	
	for _, pattern := range patterns {
		re := regexp.MustCompile(`(?i)` + pattern)
		matches := re.FindStringSubmatch(htmlContent)
		if len(matches) > 1 && matches[1] != "" {
			return strings.TrimSpace(matches[1])
		}
	}
	
	return ""
}

// detectCharsetByHeuristics uses simple heuristics to detect encoding
func detectCharsetByHeuristics(data []byte, verbose bool) string {
	// Check for common patterns that indicate Chinese content
	if containsChinese(data) {
		if verbose {
			log.Printf("Detected Chinese characters, trying GBK/GB18030")
		}
		// For Chinese content, try GBK first as it's more common
		if isValidGBK(data) {
			return "gbk"
		}
		return "gb18030"
	}
	
	// Check for Japanese patterns
	if containsJapanese(data) {
		if verbose {
			log.Printf("Detected Japanese characters, trying Shift_JIS")
		}
		return "shift_jis"
	}
	
	// Check for Korean patterns  
	if containsKorean(data) {
		if verbose {
			log.Printf("Detected Korean characters, trying EUC-KR")
		}
		return "euc-kr"
	}
	
	return ""
}

// containsChinese checks if data contains Chinese characters
func containsChinese(data []byte) bool {
	// Look for common GBK/GB18030 byte patterns
	for i := 0; i < len(data)-1; i++ {
		b1, b2 := data[i], data[i+1]
		// GBK high byte range
		if (b1 >= 0xA1 && b1 <= 0xFE) && (b2 >= 0xA1 && b2 <= 0xFE) {
			return true
		}
		// GB18030 extended range
		if (b1 >= 0x81 && b1 <= 0xFE) && (b2 >= 0x40 && b2 <= 0xFE && b2 != 0x7F) {
			return true
		}
	}
	return false
}

// containsJapanese checks if data contains Japanese characters
func containsJapanese(data []byte) bool {
	// Look for Shift_JIS patterns
	for i := 0; i < len(data)-1; i++ {
		b1, b2 := data[i], data[i+1]
		// Shift_JIS first byte ranges
		if ((b1 >= 0x81 && b1 <= 0x9F) || (b1 >= 0xE0 && b1 <= 0xFC)) &&
			((b2 >= 0x40 && b2 <= 0x7E) || (b2 >= 0x80 && b2 <= 0xFC)) {
			return true
		}
	}
	return false
}

// containsKorean checks if data contains Korean characters
func containsKorean(data []byte) bool {
	// Look for EUC-KR patterns
	for i := 0; i < len(data)-1; i++ {
		b1, b2 := data[i], data[i+1]
		// EUC-KR range
		if (b1 >= 0xA1 && b1 <= 0xFE) && (b2 >= 0xA1 && b2 <= 0xFE) {
			// This overlaps with Chinese, so we need additional heuristics
			// Korean has different character frequency patterns
			return true
		}
	}
	return false
}

// isValidGBK checks if data is valid GBK encoding
func isValidGBK(data []byte) bool {
	decoder := simplifiedchinese.GBK.NewDecoder()
	reader := decoder.Reader(bytes.NewReader(data))
	_, err := io.ReadAll(reader)
	return err == nil
}

// normalizeCharsetName normalizes charset names for better matching
func normalizeCharsetName(charset string) string {
	charset = strings.ToLower(strings.TrimSpace(charset))
	
	// Common aliases
	switch charset {
	case "gb2312", "gb_2312", "gb_2312-80", "euc-cn":
		return "gbk" // GBK is a superset of GB2312
	case "gb18030", "gb-18030":
		return "gb18030"
	case "gbk", "cp936", "ms936":
		return "gbk"
	case "big5", "cp950", "big5-hkscs":
		return "big5"
	case "shift_jis", "shift-jis", "sjis", "cp932", "ms932":
		return "shift_jis"
	case "euc-jp", "eucjp":
		return "euc-jp"
	case "euc-kr", "euckr", "cp949":
		return "euc-kr"
	case "iso-2022-jp":
		return "iso-2022-jp"
	case "utf-8", "utf8":
		return "utf-8"
	case "utf-16", "utf16":
		return "utf-16"
	case "utf-16le", "utf16le":
		return "utf-16le"
	case "utf-16be", "utf16be":
		return "utf-16be"
	case "windows-1252", "cp1252":
		return "windows-1252"
	case "iso-8859-1", "latin1":
		return "iso-8859-1"
	default:
		return charset
	}
}

// isUTF8Charset checks if the charset is already UTF-8
func isUTF8Charset(charset string) bool {
	normalized := normalizeCharsetName(charset)
	return normalized == "utf-8" || normalized == "utf8"
}

// convertToUTF8 converts data from the specified charset to UTF-8
func convertToUTF8(data []byte, fromCharset string) ([]byte, error) {
	var decoder *encoding.Decoder
	
	switch normalizeCharsetName(fromCharset) {
	case "gbk":
		decoder = simplifiedchinese.GBK.NewDecoder()
	case "gb18030":
		decoder = simplifiedchinese.GB18030.NewDecoder()
	case "hzgb2312":
		decoder = simplifiedchinese.HZGB2312.NewDecoder()
	case "big5":
		decoder = traditionalchinese.Big5.NewDecoder()
	case "shift_jis":
		decoder = japanese.ShiftJIS.NewDecoder()
	case "euc-jp":
		decoder = japanese.EUCJP.NewDecoder()
	case "iso-2022-jp":
		decoder = japanese.ISO2022JP.NewDecoder()
	case "euc-kr":
		decoder = korean.EUCKR.NewDecoder()
	case "utf-16":
		decoder = unicode.UTF16(unicode.BigEndian, unicode.UseBOM).NewDecoder()
	case "utf-16le":
		decoder = unicode.UTF16(unicode.LittleEndian, unicode.IgnoreBOM).NewDecoder()
	case "utf-16be":
		decoder = unicode.UTF16(unicode.BigEndian, unicode.IgnoreBOM).NewDecoder()
	case "windows-1252":
		decoder = charmap.Windows1252.NewDecoder()
	case "iso-8859-1":
		decoder = charmap.ISO8859_1.NewDecoder()
	default:
		return nil, fmt.Errorf("unsupported charset: %s", fromCharset)
	}
	
	// Convert the data
	reader := decoder.Reader(bytes.NewReader(data))
	converted, err := io.ReadAll(reader)
	if err != nil {
		return nil, fmt.Errorf("failed to convert from %s: %w", fromCharset, err)
	}
	
	return converted, nil
} 