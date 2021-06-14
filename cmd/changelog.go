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
		Sections    []ChangeSection
	}{
		changelog.Version,
		changelog.ReleaseDate.Format("02-01-2006"),
		changelog.Sections,
	}

	return tmpl.Execute(w, data)
}

func buildSections(changesDir string) ([]ChangeSection, error) {
	changes, err := findChanges(changesDir)
	if err != nil {
		return nil, err
	}

	types := make([]string, len(changes))
	for t := range changes {
		types = append(types, t)
	}
	sort.Strings(types)

	sections := make([]ChangeSection, len(changes))
	for _, ctype := range types {
		section := ChangeSection{
			Type:    strings.Title(ctype),
			Changes: changes[ctype],
		}
		sections = append(sections, section)
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

		ctype := parts[1]
		bytes, err := ioutil.ReadFile(filepath.Join(changesDir, filename))
		if err != nil {
			return nil, err
		}

		change := Change{IssueNumber: issue, Content: string(bytes)}
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
- {{ .Content }} (` + "`{{ .IssueNumber }} <https://github.com/example/project/issues/{{ .IssueNumber }}>`_" + `)
{{- end }}

{{ end }}
`

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
