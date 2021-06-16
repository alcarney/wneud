package cmd

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

const VERSION = "0.1.0"

func init() {

	viper.SetDefault("github_repository", "example/repo")

	viper.BindEnv("github_repository")

	rootCmd.AddCommand(changelogCmd)
	rootCmd.AddCommand(versionCmd)
}

var rootCmd = &cobra.Command{
	Use:   "wneud",
	Short: "wneud is a tool for automating software releases and going project managment",
}

var changelogCmd = &cobra.Command{
	Use:   "changelog",
	Short: "Write a draft changelog entry for the next release",
	Run: func(cmd *cobra.Command, args []string) {

		repository := viper.GetString("github_repository")
		fmt.Printf("It is: '%s'", repository)
		changelog, err := BuildChangelog(repository, "changes", time.Now())
		if err != nil {
			log.Fatalf("Unable to find changelog entries, %s\n", err)
		}

		err = changelog.asRst(os.Stdout)
		if err != nil {
			log.Fatalf("Unable to write changelog, %s", err)
		}
	},
}

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print version number and exit",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("v" + VERSION)
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
