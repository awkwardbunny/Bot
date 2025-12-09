# Signal Bot

Signal bot for myself.

Commands:
- `!help`: Lists available commands and descriptions.
- `!todo`: Print out message onto receipt paper.

Uses [filipre/signalbot](https://github.com/filipre/signalbot), which requires [bbernhard/signal-rest-api](https://github.com/bbernhard/signal-cli-rest-api) to be set up.  
Also uses [Python-ESCPOS](https://github.com/python-escpos/python-escpos) to communicate with the printer.

## Commands

Currently, only 1 real command exists, which is what this project was built for, but can be easily extended.

#### Command: TODO

Send a message starting with `!todo`, optionally with image attachments, and it will print it out onto a receipt paper. Once it is printed and cut, the bot will react to the message with the little printer emoji.

The ESCPOS library supports various modes for connecting to the printer.  
I've originally used USB on a Linux box and had the `device` in the config to be `/dev/usb/lp0`, but wanting to move it to a Docker container on my server, hooked up the printer to the network instead. You may also have to change line 53 from `Network` to `File` (as well as the import).

![screenshot](/docs/todo_screenshot.png)
![screenshot](/docs/printer.png)

#### Actual TODO regarding this project
- Add docs explaining setup.
- Optionally accept ENV variables over values in config.json