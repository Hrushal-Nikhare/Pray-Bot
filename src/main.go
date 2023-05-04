package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	// Get the token from the environment variable
	token := os.Getenv("DISCORD_TOKEN")
	if token == "" {
		log.Fatal("No token provided")
	}

	// Create a new Discord session using the bot token
	dg, err := discordgo.New("Bot " + token)
	if err != nil {
		log.Fatal("Error creating Discord session:", err)
		return
	}

	// Register the slash command handler function
	dg.AddHandler(slashCommandHandler)

	// Open the websocket and begin listening
	err = dg.Open()
	if err != nil {
		log.Fatal("Error opening connection:", err)
		return
	}

	fmt.Printf("Logged in as %s (ID: %s)\nPress CTRL-C to exit.\n------\n", dg.State.User.Username, dg.State.User.ID)

	var (
		guildID    string
		channel_id string
	)
	mode := "prod"
	if mode == "test" {
		guildID = "834371471891496960" // Testing guild
		channel_id = "1090865789877366794"
	} else {
		guildID = "856266812605988915" // Execute big guild
		channel_id = "856266813322428419"
	}

	_, err = dg.ApplicationCommandCreate(dg.State.User.ID, guildID, &discordgo.ApplicationCommand{
		Name:        "set_pray",
		Description: "Sets a job to send a message to the current channel at a specific time.",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionUser,
				Name:        "user",
				Description: "The user to add the job for.",
				Required:    false,
			},
		},
	})
	if err != nil {
		log.Fatal("Error creating slash command:", err)
		return
	}

	log.Println("Slash command registered")
	// make one webhook to send all the messages with
	webhook, err := dg.WebhookCreate(channel_id, "Pray Bot Web Hook", "")
	if err != nil {
		log.Fatal("Unable to create webhook", err)
	}

	// send pray message every 12 hours
	ticker := time.NewTicker(12 * time.Hour) // create a ticker that ticks every 12 hours
	quit := make(chan struct{})              // create a quit channel to stop the ticker
	go func() {
		for {
			select {
			case <-ticker.C: // do stuff when the ticker ticks
				file, _ := os.Open("/home/carboncap/Pray-Bot/src/users.json")
				defer file.Close()
				decoder := json.NewDecoder(file)
				var array []string
				decoder.Decode(&array)
				for _, v := range array {
					user, _ := dg.User(v)
					// generate a random number between 900 and 3600 and convert it to seconds
					d := time.Duration(rand.Intn(2701)+900) * time.Second
					time.Sleep(d)
					dg.WebhookExecute(webhook.ID, webhook.Token, true, &discordgo.WebhookParams{
						Content:   ":pray:",
						Username:  user.Username,
						AvatarURL: user.AvatarURL(""),
					})
				}
			case <-quit: // stop the ticker when the quit channel is closed
				ticker.Stop()
				return
			}
		}
	}()

	// Wait for a CTRL-C signal to stop the bot
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc
	// Stop the ticker
	close(quit)
	// Delete the webhook
	dg.WebhookDelete(webhook.ID)
	log.Println("Exiting...")

	// Close the Discord session
	dg.Close()
}

// This function handles slash command interactions
func slashCommandHandler(s *discordgo.Session, i *discordgo.InteractionCreate) {
	if i.Type == discordgo.InteractionApplicationCommand && i.ApplicationCommandData().Name == "set_pray" {
		// get the user from the interaction
		var user *discordgo.User
		if len(i.ApplicationCommandData().Options) > 0 {
			user = i.ApplicationCommandData().Options[0].UserValue(s)
		} else {
			user = i.Member.User
		}
		// Open file to add user to
		file, _ := os.Open("/home/carboncap/Pray-Bot/src/users.json")
		defer file.Close()
		decoder := json.NewDecoder(file)

		// create a golang slice to hold the decoded array
		var array []string

		// decode the JSON array into the slice
		decoder.Decode(&array)

		// append the user to the slice
		array = append(array, user.ID)

		// encode the slice to write back to the file
		jsonBytes, _ := json.Marshal(array)

		// Write to file
		os.WriteFile("/home/carboncap/Pray-Bot/src/users.json", jsonBytes, 0644)

		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Content: fmt.Sprintf("Done! added %s#%s to the list", user.Username, user.Discriminator),
				Flags:   discordgo.MessageFlagsEphemeral, // Make the message only visible to the author
			},
		})
	}
}
