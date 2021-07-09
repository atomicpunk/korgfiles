# korgfiles

KORG File Extractor

Extract Korg data files from a disk image or device

This tool is designed to recover korg data files from old disks and disk
images that may no longer be mountable. The tool takes in the path of a
disk image or the device id of an unmounted partition and searches the disk
for files, whether they've been deleted ot not.

The tool is run on any of five types of korg files: SNG, PCG, KSC, KSF, KMP.
The extracted files are placed in the current folder, and any name collisions
are handled by appending digits to the newer versions.

[Korg SNG files]

Thes files include midi note data.

Korg sng files have built in name and size encoding so they're relatively
easy to extract. As long as the header is intact the file should be recoverable.

%> korgfiles diskimage sng

[Korg PCG files]

These files include instrument and effect data.

Korg pcg files have built in size encoding but their names are only stored in the
FAT. Thus when PCG files are extracted they're simply named "KORG.PCG". You'll
have to load them to figure out which songs they pair with.

%> korgfiles diskimage pcg

[Korg KSF files]

These files include wav sound data.

Korg ksf files have built in name and size encoding so they're relatively
easy to extract. As long as the header is intact the file should be recoverable.
However, since many of the files recovered may have been deleted and partially
overwritten, the tool attempts to identify damaged KSF files. These are files
whose sizes don't match but have at least some usable sound data in them. They're
saved as NAME-DMG.KSF to differentiate between the complete files.

%> korgfiles diskimage ksf

[Korg KSC files]

These files are simple text scripts for loading KSF data.

Korg ksc files are just text files, so they're fairly easy to identify. The
output KSC file may occasionally have some junk data if it was partially
overwritten after delete, but they can be editted in a text editor.

%> korgfiles diskimage ksc

[Korg KMP files]

These files are key maps for mapping KSF data to keys.

Korg kmp files are the hardest to retrieve since they have no size info. The
tool just does its best to identify the end of the KMP file but it may
occasionally have junk at the end. These files typically aren't very useful
anyway because they depend on fixed ksf filenames which this tool cannot retrieve.

%> korgfiles diskimage kmp
