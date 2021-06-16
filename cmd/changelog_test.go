package cmd

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"path/filepath"
	"testing"
	"time"

	"github.com/sergi/go-diff/diffmatchpatch"
)

func TestBuildSections(t *testing.T) {
	content, err := ioutil.ReadFile(filepath.Join("testdata", "changes", "CHANGES.rst"))
	if err != nil {
		t.Fatalf("Unexpected error, %s", err)
	}

	expected := string(content)

	releaseDate, err := time.Parse("02-01-2006", "01-02-2020")
	if err != nil {
		t.Fatalf("Unexpected error, %s", err)
	}

	changelog, err := BuildChangelog("example/project", filepath.Join("testdata", "changes"), releaseDate)
	if err != nil {
		t.Fatalf("Unexpected error, %s", err)
	}

	var buf bytes.Buffer
	err = changelog.asRst(&buf)
	if err != nil {
		t.Fatalf("Unexpected error, %s", err)
	}

	actual := buf.String()

	if expected != actual {
		fmt.Printf("Length %d vs %d", len(expected), len(actual))
		dmp := diffmatchpatch.New()
		diffs := dmp.DiffMain(expected, actual, false)
		t.Fatalf(dmp.DiffPrettyText(diffs))
	}

}
