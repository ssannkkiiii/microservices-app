package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
)

type TranslationRequest struct {
	Text       string `json:"text"`
	SourceLang string `json:"source_lang"`
	TargetLang string `json:"target_lang"`
	RequestID  string `json:"request_id"`
}

type TranslationResponse struct {
	RequestID      string `json:"request_id"`
	OriginalText   string `json:"original_text"`
	TranslatedText string `json:"translated_text"`
	SourceLang     string `json:"source_lang"`
	TargetLang     string `json:"target_lang"`
}

// Маппінг кодів мов для API перекладу
var langCodes = map[string]string{
	"en": "en",
	"uk": "uk",
	"ru": "ru",
	"de": "de",
	"fr": "fr",
}

func translate(text, src, dest string) string {
	textTrimmed := strings.TrimSpace(text)
	if textTrimmed == "" {
		return text
	}

	if src == dest {
		return text
	}

	srcCode, ok := langCodes[src]
	if !ok {
		srcCode = src
	}
	destCode, ok := langCodes[dest]
	if !ok {
		destCode = dest
	}

	translated, err := translateWithAPI(textTrimmed, srcCode, destCode)
	if err != nil {
		log.Printf("Translation API error: %v, falling back to placeholder", err)
		return fmt.Sprintf("[%s→%s] %s", strings.ToUpper(src), strings.ToUpper(dest), textTrimmed)
	}

	return translated
}

func translateWithAPI(text, srcLang, destLang string) (string, error) {
	apiURL := "https://api.mymemory.translated.net/get"

	params := url.Values{}
	params.Add("q", text)
	params.Add("langpair", fmt.Sprintf("%s|%s", srcLang, destLang))

	fullURL := fmt.Sprintf("%s?%s", apiURL, params.Encode())

	client := &http.Client{
		Timeout: 10 * time.Second,
	}

	resp, err := client.Get(fullURL)
	if err != nil {
		return "", fmt.Errorf("HTTP request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API returned status %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	var result struct {
		ResponseData struct {
			TranslatedText string `json:"translatedText"`
		} `json:"responseData"`
		ResponseStatus  int    `json:"responseStatus"`
		ResponseDetails string `json:"responseDetails,omitempty"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		return "", fmt.Errorf("failed to parse JSON: %w", err)
	}

	if result.ResponseStatus != 200 {
		return "", fmt.Errorf("API returned status %d: %s", result.ResponseStatus, result.ResponseDetails)
	}

	translated := result.ResponseData.TranslatedText
	if translated == "" {
		return "", fmt.Errorf("empty translation received")
	}

	translated = strings.TrimSpace(translated)

	if strings.EqualFold(translated, text) && result.ResponseStatus == 200 {
		log.Printf("Translation returned same text, might be accurate or API limitation")
	}

	return translated, nil
}

func failOnError(err error, msg string) {
	if err != nil {
		log.Fatalf("%s: %s", msg, err)
	}
}

func main() {
	var conn *amqp.Connection
	var err error

	maxRetries := 10
	for i := 0; i < maxRetries; i++ {
		conn, err = amqp.Dial("amqp://guest:guest@rabbitmq:5672/")
		if err == nil {
			break
		}
		log.Printf("Attempt %d/%d: Failed to connect to RabbitMQ: %v", i+1, maxRetries, err)
		if i < maxRetries-1 {
			time.Sleep(time.Duration(1<<uint(i)) * time.Second)
		}
	}
	failOnError(err, "Failed to connect to RabbitMQ after retries")
	defer conn.Close()

	ch, err := conn.Channel()
	failOnError(err, "Failed to open channel")
	defer ch.Close()

	_, err = ch.QueueDeclare("translate_requests", true, false, false, false, nil)
	failOnError(err, "Failed to declare requests queue")

	msgs, err := ch.Consume("translate_requests", "", true, false, false, false, nil)
	failOnError(err, "Failed to register a consumer")

	fmt.Println("🐹 Go worker started, waiting for messages...")

	for d := range msgs {
		var req TranslationRequest
		if err := json.Unmarshal(d.Body, &req); err != nil {
			log.Println("Invalid request body:", err)
			continue
		}

		translated := translate(req.Text, req.SourceLang, req.TargetLang)
		log.Printf("🔤 Translation: '%s' [%s→%s] = '%s'", req.Text, req.SourceLang, req.TargetLang, translated)

		resp := TranslationResponse{
			RequestID:      req.RequestID,
			OriginalText:   req.Text,
			TranslatedText: translated,
			SourceLang:     req.SourceLang,
			TargetLang:     req.TargetLang,
		}

		body, _ := json.Marshal(resp)

		replyTo := d.ReplyTo
		if replyTo == "" {
			replyTo = "translate_responses"
		}

		err = ch.PublishWithContext(
			context.Background(),
			"",
			replyTo,
			false,
			false,
			amqp.Publishing{
				ContentType:   "application/json",
				Body:          body,
				CorrelationId: d.CorrelationId,
			},
		)
		if err != nil {
			log.Println("Failed to publish response:", err)
		} else {
			fmt.Printf("✅ [%s->%s] published to %s (corr=%s)\n", req.SourceLang, req.TargetLang, replyTo, d.CorrelationId)
		}
	}
}
