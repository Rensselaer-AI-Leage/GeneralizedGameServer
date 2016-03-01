# GeneralizedGameServer
A server for hosting AI-programming competitions.
<br>
Design principles:
<ul>
    <li>Keep everything as general as possible so that switching games is as easy as changing one line of code.</li>
    <li>Keep as much of the client-server communication hidden as possible. Competitors should only have to worry about their bot's logic.</li>
    <li>Keep each client's communication with the server confidential</li>
</ul>
<br>
In Server directory:
<ul>
    <li>ai_server.py - Server class, keeps track of active connections, handles matchmaking, and communicates with all clients</li>
    <li>do_rps.py - Game logic for Rock-Paper-Scissors.</li>
    <li>run_server.py - Sets up the server to run with the correct game logic</li>
</ul>
<br>
In Template directory:
<ul>
    <li>helper.py - BotHelper class, handles communication with the server so contestants don't need to worry about socket programming.</li>
    <li>template.py - Template for contestants to use. Ideally, all the contestant needs to do is edit the strategy function.</li>
</ul>
<br>
In both directories:
<ul>
    <li>message.py - API for client-server communication. Provides functions for sending and receiving code. Authentication, encoding, and decoding handled automatically.</li>
</ul>
