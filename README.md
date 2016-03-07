# Generalized Game Server
<p>A server for hosting AI-programming competitions.</p>

<p>It is worthy to note that this program is still under heavy development. While it should work for the RPS competition at this point, more functionality needs to be added for it to be suitable for more complicated games.</p>

<p>Design principles:
<ul>
    <li>Keep everything as general as possible so that switching games is as easy as changing one line of code.</li>
    <li>Keep as much of the client-server communication hidden as possible. Competitors should only have to worry about their bot's logic.</li>
    <li>Keep each client's communication with the server confidential</li>
</ul>
</p>

<p>Explanations of packages:
<ul>
    <li>client: Any resources specific to competitors, including templates and helper classes</li>
    <li>helpers: Any resource used by both the server and client, including file I/O and client-server interaction helpers</li>
    <li>host: Any resource specific to the server, including actual server code and game logic</li>
</ul>
</p>
