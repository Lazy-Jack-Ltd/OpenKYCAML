// Package main provides the OpenKYCAML Go validator.
//
// Validates JSON payloads against the OpenKYCAML schema (JSON Schema draft 2020-12).
// Designed for TRISA and other Go-native Travel Rule integrations.
//
// Usage:
//
//	go run . <path/to/payload.json>
//	go run . --stdin < payload.json
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/santhosh-tekuri/jsonschema/v6"
)

// schemaPath returns the absolute path to the bundled OpenKYCAML schema,
// resolved relative to this source file's location so the validator works
// regardless of the working directory from which it is invoked.
func schemaPath() string {
	_, file, _, ok := runtime.Caller(0)
	if !ok {
		// Fallback: assume we are run from tools/go/
		return filepath.Join("..", "..", "schema", "kyc-aml-hybrid-extended.json")
	}
	dir := filepath.Dir(file)
	return filepath.Join(dir, "..", "..", "schema", "kyc-aml-hybrid-extended.json")
}

// ValidationResult holds the outcome of validating a single payload.
type ValidationResult struct {
	IsValid  bool
	Errors   []string
	Warnings []string
}

// OpenKYCAMLValidator validates JSON payloads against the OpenKYCAML schema.
type OpenKYCAMLValidator struct {
	compiler *jsonschema.Compiler
	schema   *jsonschema.Schema
}

// NewOpenKYCAMLValidator creates a validator using the bundled schema at the
// default path (../../schema/kyc-aml-hybrid-extended.json relative to this file).
func NewOpenKYCAMLValidator() (*OpenKYCAMLValidator, error) {
	return NewOpenKYCAMLValidatorFromPath(schemaPath())
}

// NewOpenKYCAMLValidatorFromPath creates a validator using a schema at the
// given file path. Useful for testing and custom schema versions.
func NewOpenKYCAMLValidatorFromPath(path string) (*OpenKYCAMLValidator, error) {
	absPath, err := filepath.Abs(path)
	if err != nil {
		return nil, fmt.Errorf("resolving schema path: %w", err)
	}

	compiler := jsonschema.NewCompiler()
	schema, err := compiler.Compile(absPath)
	if err != nil {
		return nil, fmt.Errorf("compiling schema %q: %w", absPath, err)
	}

	return &OpenKYCAMLValidator{compiler: compiler, schema: schema}, nil
}

// Validate validates a decoded JSON payload (map[string]any or equivalent).
// Returns a ValidationResult; IsValid is true iff there are no schema errors.
func (v *OpenKYCAMLValidator) Validate(payload any) ValidationResult {
	err := v.schema.Validate(payload)
	if err == nil {
		warnings := businessWarnings(payload)
		return ValidationResult{IsValid: true, Warnings: warnings}
	}

	var errs []string
	if ve, ok := err.(*jsonschema.ValidationError); ok {
		errs = []string{ve.Error()}
	} else {
		errs = []string{err.Error()}
	}

	return ValidationResult{IsValid: false, Errors: errs}
}

// businessWarnings emits advisory warnings for common compliance oversights.
// These are not schema violations but may indicate incomplete or risky data.
func businessWarnings(payload any) []string {
	m, ok := payload.(map[string]any)
	if !ok {
		return nil
	}

	var warns []string

	// Tax status ESR and Pillar 2 warnings (v1.9.0).
	taxRaw, hasTax := m["taxStatus"]
	if hasTax {
		tax, ok := taxRaw.(map[string]any)
		if ok {
			// ESR non-compliance warning.
			if esrRaw, ok := tax["economicSubstance"]; ok {
				if esr, ok := esrRaw.(map[string]any); ok {
					if status, _ := esr["status"].(string); status == "nonCompliant" {
						jur, _ := esr["jurisdiction"].(string)
						if jur == "" {
							jur = "unknown"
						}
						warns = append(warns,
							fmt.Sprintf(
								"taxStatus.economicSubstance.status is 'nonCompliant' for jurisdiction '%s' — "+
									"ESR non-compliance is a direct AML red flag under AMLR Art. 26 and EBA ML/TF "+
									"risk-factor guidelines. EDD is required; consider SAR filing.",
								jur,
							),
						)
					}
				}
			}

			// Pillar 2 GIR reference missing warning.
			if p2Raw, ok := tax["pillarTwo"]; ok {
				if p2, ok := p2Raw.(map[string]any); ok {
					inScope, _ := p2["inScopeMNE"].(bool)
					girRef, _ := p2["girFilingReference"].(string)
					if inScope && strings.TrimSpace(girRef) == "" {
						warns = append(warns,
							"taxStatus.pillarTwo.inScopeMNE is true but girFilingReference is absent — "+
								"in-scope MNEs must file a GloBE Information Return (GIR). "+
								"Request the GIR reference and perform enhanced due diligence.",
						)
					}
				}
			}
		}
	}

	return warns
}

// ValidateReader validates a JSON payload read from an io.Reader.
func (v *OpenKYCAMLValidator) ValidateReader(r io.Reader) ValidationResult {
	var payload any
	if err := json.NewDecoder(r).Decode(&payload); err != nil {
		return ValidationResult{
			IsValid: false,
			Errors:  []string{fmt.Sprintf("JSON parse error: %s", err)},
		}
	}
	return v.Validate(payload)
}

// ValidateFile validates a JSON payload read from a file at the given path.
func (v *OpenKYCAMLValidator) ValidateFile(path string) ValidationResult {
	f, err := os.Open(path)
	if err != nil {
		return ValidationResult{
			IsValid: false,
			Errors:  []string{fmt.Sprintf("cannot open file %q: %s", path, err)},
		}
	}
	defer f.Close()
	return v.ValidateReader(f)
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

func main() {
	useStdin := flag.Bool("stdin", false, "Read JSON payload from stdin instead of a file.")
	schemaOverride := flag.String("schema", "", "Path to a custom OpenKYCAML schema file.")
	flag.Parse()

	var validator *OpenKYCAMLValidator
	var err error

	if *schemaOverride != "" {
		validator, err = NewOpenKYCAMLValidatorFromPath(*schemaOverride)
	} else {
		validator, err = NewOpenKYCAMLValidator()
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading schema: %s\n", err)
		os.Exit(2)
	}

	var result ValidationResult

	if *useStdin {
		result = validator.ValidateReader(os.Stdin)
	} else {
		args := flag.Args()
		if len(args) == 0 {
			fmt.Fprintln(os.Stderr, "Usage: go run . [--stdin] [--schema PATH] <payload.json>")
			os.Exit(2)
		}
		result = validator.ValidateFile(args[0])
	}

	if result.IsValid {
		fmt.Println("VALID")
		for _, w := range result.Warnings {
			fmt.Fprintf(os.Stderr, "  WARNING: %s\n", w)
		}
		os.Exit(0)
	}

	fmt.Fprintf(os.Stderr, "INVALID — %d error(s):\n", len(result.Errors))
	for _, e := range result.Errors {
		fmt.Fprintf(os.Stderr, "  %s\n", e)
	}
	os.Exit(1)
}
