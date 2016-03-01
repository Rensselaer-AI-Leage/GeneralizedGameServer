# GeneralizedGameServer
A server for hosting AI-programming competitions.

Design principles:
    -Keep everything as general as possible so that switching games is as easy as changing one line of code.
    -Keep as much of the client-server communication hidden as possible. Competitors should only have to worry about their bot's logic.
    -Keep each client's communication with the server confidential

In Server directory:
    ai_server.py - Server class, keeps track of active connections, handles matchmaking, and communicates with all clients
    do_rps.py - Game logic for Rock-Paper-Scissors.
    run_server.py - Sets up the server to run with the correct game logic

In Template directory:
    helper.py - BotHelper class, handles communication with the server so contestants don't need to worry about socket programming.
    template.py - Template for contestants to use. Ideally, all the contestant needs to do is edit the strategy function.

In both directories:
    message.py - API for client-server communication. Provides functions for sending and receiving code. Authentication, encoding, and decoding handled automatically.
