# edce-client
Elite Dangerous Companion Emulator

## Purpose

This is an interface that emulates an iPhone accessing the Elite Dangerous Companion, which is a mobile application developed by Frontier Developments. This experimental code has not been created in association with [Frontier Developments](http://www.frontier.co.uk/) and is unsupported by them.


## Installation

* Requirements: Python 3.3 or higher
* Run the client-setup.py program: python3 client-setup.py
* Enter your Frontier store credentials (NOTE: The password is stored unencrypted in the edce.ini file. You can leave the password blank, however this means you will need to run the clien in interactive mode and you will be prompted to enter the password every time)

## Usage

* Launch the client: python3 edce_client.py
* The first time you run the program, the Elite Dangerous Companion website will request a verification code, which shall be sent to your account email. Enter the code at the prompt. You should only have to do this once
* The program will query your Commander's data, and dump the result in the log directory (LZMA compressed, can be examined by 7-zip)
* The program will also post the market data from the current station where your Commander is docked to [EDDN](https://github.com/jamesremuscat/EDDN/wiki). If he/she is not docked, the data is not sent.


