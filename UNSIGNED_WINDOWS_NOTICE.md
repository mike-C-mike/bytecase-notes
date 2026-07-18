# Unsigned Windows Build Notice

This ByteCase Notes pre-release build may be unsigned.

Windows SmartScreen, Microsoft Defender, or other endpoint security tools may warn when the application is downloaded or opened.

This warning can occur because:

- The executable is new.
- The executable does not yet have reputation with Microsoft SmartScreen.
- The executable is not yet signed with a trusted code signing certificate.

## Recommended verification

Only download ByteCase Notes from the official GitHub repository.

Verify the release ZIP with the published SHA-256 checksum:

```powershell
Get-FileHash .\ByteCaseNotes-v0.9.0.zip -Algorithm SHA256
```

Compare the displayed hash to `ByteCaseNotes-v0.9.0-SHA256SUMS.txt`.

## Future signing

Once a code signing certificate is available, future Windows builds should be signed before publication.
