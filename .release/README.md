# Initial release builder

The four `source.NN.b64` chunks are the reviewed release's content-deduplicated UTF-8 source snapshot, compressed with XZ. `bootstrap.py` verifies the compressed SHA-256 and every decoded file's SHA-256, checks relative paths, renders the original supplied HTML artwork, and builds the three addons plus the website. No credentials are included. Any follow-up source fix is a readable file under `overrides/`, replacing only an existing snapshot path.

The publishing workflow runs the 38 supplied integration tests on each of Odoo 17.0, 18.0, and 19.0 in disposable Docker databases. Only after every job succeeds can it atomically create the three version branches and add the website to main. It refuses existing version branches, concurrent changes, other repositories, and forced pushes. It does not publish an Odoo Apps listing or change other repositories.

Compressed source SHA-256: `a8a616fca1a9137f5db31d80427bfa540887bfd6e1927dbd9ccc99ff299757a6`.
