package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "wneud",
	Short: "wneud is a tool for automating software releases and going project managment.",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("Hi, there! %s\n", args)
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
