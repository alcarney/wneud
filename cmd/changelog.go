package cmd

import (
	"io"
	"io/ioutil"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"text/template"
	"time"
)

type Change struct {
	IssueNumber int
	Content     string
}

type ChangeSection struct {
	Type    string
	Changes []Change
}

type ChangeLog struct {
	Version     string
	ReleaseDate time.Time
	Repository  string
	Sections    []ChangeSection
}

func (changelog *ChangeLog) asRst(w io.Writer) error {
	tmpl, err := getRstTemplate()
	if err != nil {
		return err
	}

	data := struct {
		Version     string
		ReleaseDate string
		Repository  string
		Sections    []ChangeSection
	}{
		changelog.Version,
		changelog.ReleaseDate.Format("02-01-2006"),
		changelog.Repository,
		changelog.Sections,
	}

	return tmpl.Execute(w, data)
}

func BuildChangelog(repository string, changesDir string, releaseDate time.Time) (ChangeLog, error) {
	sections, err := buildSections(changesDir)
	if err != nil {
		return ChangeLog{}, nil
	}

	changelog := ChangeLog{
		Version:     "Unreleased",
		ReleaseDate: releaseDate,
		Repository:  repository,
		Sections:    sections,
	}

	return changelog, nil
}

func buildSections(changesDir string) ([]ChangeSection, error) {
	changes, err := findChanges(changesDir)
	if err != nil {
		return nil, err
	}

	types := make([]string, len(changes))
	i := 0
	for t := range changes {
		types[i] = t
		i += 1
	}
	sort.Strings(types)

	sections := make([]ChangeSection, len(types))
	for i, ctype := range types {
		section := ChangeSection{
			Type:    strings.Title(ctype),
			Changes: changes[ctype],
		}
		sections[i] = section
	}

	return sections, nil
}

func findChanges(changesDir string) (map[string][]Change, error) {

	files, err := ioutil.ReadDir(changesDir)
	if err != nil {
		return nil, err
	}

	changes := make(map[string][]Change)

	for _, file := range files {
		filename := file.Name()

		ext := filepath.Ext(filename)
		if ext != ".rst" {
			continue
		}

		name := strings.Replace(filename, ext, "", -1)
		parts := strings.Split(name, ".")

		if len(parts) != 2 {
			continue
		}

		issue, err := strconv.Atoi(parts[0])
		if err != nil {
			continue
		}

		ctype := strings.Replace(parts[1], "-", " ", -1)
		data, err := ioutil.ReadFile(filepath.Join(changesDir, filename))
		if err != nil {
			return nil, err
		}

		content := strings.Replace(string(data), "\n", "\n  ", -1)
		change := Change{IssueNumber: issue, Content: content}
		changes[ctype] = append(changes[ctype], change)
	}

	return changes, nil
}

const changelogRstTemplate = `
{{ .Version }} - {{ .ReleaseDate }}
{{ header "-" (sum (len .Version) (len .ReleaseDate) 3) }}
{{ range .Sections }}
{{ .Type }}
{{ header "^" (len .Type) }}
{{ range .Changes }}
- {{ .Content }} (` + "`{{ .IssueNumber }} <https://github.com/{{ $.Repository }}/issues/{{ .IssueNumber }}>`_" + `)
{{- end }}
{{ end }}`

func getRstTemplate() (*template.Template, error) {
	return template.New("rstChangelog").Funcs(template.FuncMap{
		"header": func(char string, length int) string {
			return strings.Repeat(char, length)
		},
		"sum": func(nums ...int) int {
			total := 0
			for _, num := range nums {
				total += num
			}
			return total
		},
	}).Parse(changelogRstTemplate)
}
