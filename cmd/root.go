package cmd

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/spf13/cobra"
)

// var isDebug = false

func init() {

	rootCmd.PersistentFlags().CountP("verbose", "v", "Increase the verbosity of the output.")
	rootCmd.AddCommand(changelogCmd)
}

var rootCmd = &cobra.Command{
	Use:              "wneud",
	PersistentPreRun: preRunHook,
	Short:            "wneud is a tool for automating software releases and going project managment.",
}

func preRunHook(cmd *cobra.Command, args []string) {
	log.SetFlags(0)

	// if getCountFlag(cmd, "verbose", 0) > 0 {
	// isDebug = true
	// }
}

var changelogCmd = &cobra.Command{
	Use:   "changelog",
	Short: "Write the changelog entry for the next release",
	Run: func(cmd *cobra.Command, args []string) {
		sections, err := buildSections("changes")
		if err != nil {
			log.Fatalf("Unable to find changelog entries, %s\n", err)
		}

		changelog := ChangeLog{
			Version:     "0.6.2",
			ReleaseDate: time.Now(),
			Sections:    sections,
		}

		changelog.asRst(os.Stdout)
	},
}

// func getCountFlag(cmd *cobra.Command, flag string, defaultValue int) int {
// 	value, err := cmd.Flags().GetCount(flag)
// 	if err != nil {
// 		return defaultValue
// 	}

// 	return value
// }

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
