# ByteCase Notes Release Checklist

Use this checklist before publishing a GitHub release.

## Source review

- [ ] Confirm `APP_VERSION` in `settings_service.py` matches the release tag.
- [ ] Confirm README version and release notes match the release tag.
- [ ] Confirm dependency list is accurate.
- [ ] Confirm no test data, case data, agency data, or personal files are included.

## Functional smoke test

- [ ] Launch app from source.
- [ ] Enter case information.
- [ ] Write narrative notes.
- [ ] Add at least one artifact.
- [ ] Use Save + Insert Ref.
- [ ] Run Check Refs.
- [ ] Export JSON.
- [ ] Export TXT.
- [ ] Export DOCX.
- [ ] Reopen saved JSON.
- [ ] Test supporting file copy.
- [ ] Test image/screenshot embedding if enabled.
- [ ] Test department patch/logo embedding if configured.

## Build test

- [ ] Run `build_release.ps1`.
- [ ] Confirm ZIP is created.
- [ ] Confirm SHA-256 checksum file is created.
- [ ] Launch EXE from release folder.
- [ ] Confirm SmartScreen/unsigned warning is expected for unsigned builds.

## GitHub release

- [ ] Create tag, for example `v0.9.0`.
- [ ] Mark as pre-release until signed/final.
- [ ] Upload release ZIP.
- [ ] Upload SHA-256 checksum file.
- [ ] Include unsigned Windows notice.
