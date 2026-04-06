package main

import (
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

// resolveExamplesDir returns the absolute path to the examples/ directory.
func resolveExamplesDir(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("runtime.Caller failed")
	}
	dir := filepath.Dir(file)
	return filepath.Join(dir, "..", "..", "examples")
}

// resolveSchemaPath returns the absolute path to the bundled schema.
func resolveSchemaPath(t *testing.T) string {
	t.Helper()
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("runtime.Caller failed")
	}
	dir := filepath.Dir(file)
	return filepath.Join(dir, "..", "..", "schema", "kyc-aml-hybrid-extended.json")
}

func newTestValidator(t *testing.T) *OpenKYCAMLValidator {
	t.Helper()
	v, err := NewOpenKYCAMLValidatorFromPath(resolveSchemaPath(t))
	if err != nil {
		t.Fatalf("failed to create validator: %v", err)
	}
	return v
}

// ---------------------------------------------------------------------------
// Schema loading
// ---------------------------------------------------------------------------

func TestNewOpenKYCAMLValidatorFromPath_ValidSchema(t *testing.T) {
	_, err := NewOpenKYCAMLValidatorFromPath(resolveSchemaPath(t))
	if err != nil {
		t.Fatalf("expected no error loading schema, got: %v", err)
	}
}

func TestNewOpenKYCAMLValidatorFromPath_NonExistentFile(t *testing.T) {
	_, err := NewOpenKYCAMLValidatorFromPath("/nonexistent/schema.json")
	if err == nil {
		t.Fatal("expected error for non-existent schema file, got nil")
	}
}

// ---------------------------------------------------------------------------
// Valid payloads
// ---------------------------------------------------------------------------

func TestValidate_MinimalValidPayload(t *testing.T) {
	v := newTestValidator(t)
	payload := map[string]any{
		"$schema":         "https://openkycaml.org/schema/v1.3.0/kyc-aml-hybrid-extended.json",
		"version":         "1.3.0",
		"messageId":       "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
		"messageDateTime": "2026-01-01T00:00:00Z",
		"ivms101": map[string]any{
			"originator": map[string]any{
				"originatorPersons": []any{
					map[string]any{
						"naturalPerson": map[string]any{
							"name": map[string]any{
								"nameIdentifier": []any{
									map[string]any{
										"primaryIdentifier":   "Smith",
										"secondaryIdentifier": "Jane",
										"nameIdentifierType":  "LEGL",
									},
								},
							},
							"nationalIdentification": map[string]any{
								"nationalIdentifier":     "DE-123456789",
								"nationalIdentifierType": "CCPT",
							},
							"countryOfResidence": "DE",
						},
					},
				},
				"accountNumber": []any{"0xABCDEF1234567890ABCDEF1234567890ABCDEF12"},
			},
			"beneficiary": map[string]any{
				"beneficiaryPersons": []any{
					map[string]any{
						"naturalPerson": map[string]any{
							"name": map[string]any{
								"nameIdentifier": []any{
									map[string]any{
										"primaryIdentifier":   "Jones",
										"secondaryIdentifier": "Bob",
										"nameIdentifierType":  "LEGL",
									},
								},
							},
						},
					},
				},
				"accountNumber": []any{"0x9876543210ABCDEF9876543210ABCDEF98765432"},
			},
			"originatingVASP": map[string]any{
				"vasp": map[string]any{
					"legalPerson": map[string]any{
						"name": map[string]any{
							"nameIdentifier": []any{
								map[string]any{
									"legalPersonName":                "Acme Crypto Exchange BV",
									"legalPersonNameIdentifierType":  "LEGL",
								},
							},
						},
						"nationalIdentification": map[string]any{
							"nationalIdentifier":     "529900T8BM49AURSDO55",
							"nationalIdentifierType": "LEIX",
						},
						"countryOfRegistration": "NL",
					},
				},
			},
			"beneficiaryVASP": map[string]any{
				"vasp": map[string]any{
					"legalPerson": map[string]any{
						"name": map[string]any{
							"nameIdentifier": []any{
								map[string]any{
									"legalPersonName":               "Fintech Exchange Ltd",
									"legalPersonNameIdentifierType": "LEGL",
								},
							},
						},
						"nationalIdentification": map[string]any{
							"nationalIdentifier":     "213800QILIUD4ROSUO03",
							"nationalIdentifierType": "LEIX",
						},
						"countryOfRegistration": "GB",
					},
				},
			},
			"transferredAmount": map[string]any{
				"amount":    "1.5",
				"assetType": "ETH",
			},
		},
	}

	result := v.Validate(payload)
	if !result.IsValid {
		t.Errorf("expected valid payload to pass, got errors: %v", result.Errors)
	}
}

// ---------------------------------------------------------------------------
// Invalid payloads
// ---------------------------------------------------------------------------

func TestValidate_EmptyObjectFails(t *testing.T) {
	v := newTestValidator(t)
	result := v.Validate(map[string]any{})
	if result.IsValid {
		t.Error("expected empty payload to fail validation")
	}
	if len(result.Errors) == 0 {
		t.Error("expected at least one error")
	}
}

func TestValidate_MissingRequiredFieldsFails(t *testing.T) {
	v := newTestValidator(t)
	result := v.Validate(map[string]any{"version": "1.3.0"})
	if result.IsValid {
		t.Error("expected payload missing required fields to fail")
	}
}

// ---------------------------------------------------------------------------
// ValidateReader
// ---------------------------------------------------------------------------

func TestValidateReader_InvalidJSON(t *testing.T) {
	v := newTestValidator(t)
	result := v.ValidateReader(strings.NewReader("{not json}"))
	if result.IsValid {
		t.Error("expected invalid JSON to fail")
	}
	if len(result.Errors) == 0 {
		t.Error("expected at least one error")
	}
}

// ---------------------------------------------------------------------------
// ValidateFile — examples
// ---------------------------------------------------------------------------

func TestValidateFile_MinimalTravelRuleExample(t *testing.T) {
	v := newTestValidator(t)
	examplesDir := resolveExamplesDir(t)
	result := v.ValidateFile(filepath.Join(examplesDir, "minimal-travel-rule.json"))
	if !result.IsValid {
		t.Errorf("expected minimal-travel-rule.json to be valid, got errors: %v", result.Errors)
	}
}

func TestValidateFile_NonExistentFile(t *testing.T) {
	v := newTestValidator(t)
	result := v.ValidateFile("/nonexistent/payload.json")
	if result.IsValid {
		t.Error("expected non-existent file to produce an error result")
	}
}
