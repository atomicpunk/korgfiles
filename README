# korgfiles

KORG File Tool

$> korgfiles -h
usage: korgfiles [-h] {extract,ksf2wav} ...

positional arguments:
  {extract,ksf2wav}  command to run
    extract          extract korg files from a disk image
    ksf2wav          convert a ksf sound file to wav

optional arguments:
  -h, --help         show this help message and exit

------------------------------------------------------------------
|                          EXTRACT                               |
------------------------------------------------------------------

$> korgfiles extract -h
usage: korgfiles extract [-h] diskimage {sng,pcg,ksc,ksf,kmp}

positional arguments:
  diskimage             image file with partition data in it
  {sng,pcg,ksc,ksf,kmp}
                        korg filetype to extract

optional arguments:
  -h, --help            show this help message and exit


Extract Korg data files from a disk image (extracted from a device with dd)

$> korgfiles extract <diskimage> <filetype>

This command is designed to recover korg data files from old disks that may
no longer be mountable or with deleted data you want back. The input is a disk
image of the hard drive created using dd.

$> dd if=/dev/sda1 of=mydisk.img bs=1M

The tool takes in the path of a disk image and searches the disk for files,
whether they've been deleted ot not.

The tool is run on any of five types of korg files: SNG, PCG, KSC, KSF, KMP.
The extracted files are placed in the current folder, and any name collisions
are handled by appending digits to the newer versions.

[Korg SNG files]

Thes files include midi note data.

Korg sng files have built in name and size encoding so they're relatively
easy to extract. As long as the header is intact the file should be recoverable.

$> korgfiles extract <diskimage> sng

[Korg PCG files]

These files include instrument and effect data.

Korg pcg files have built in size encoding but their names are only stored in the
FAT. Thus when PCG files are extracted they're simply named "KORG.PCG". You'll
have to load them to figure out which songs they pair with.

$> korgfiles extract <diskimage> pcg

[Korg KSF files]

These files include wav sound data.

Korg ksf files have built in name and size encoding so they're relatively
easy to extract. As long as the header is intact the file should be recoverable.
However, since many of the files recovered may have been deleted and partially
overwritten, the tool attempts to identify damaged KSF files. These are files
whose sizes don't match but have at least some usable sound data in them. They're
saved as NAME-DMG.KSF to differentiate between the complete files.

$> korgfiles extract <diskimage> ksf

[Korg KSC files]

These files are simple text scripts for loading KSF data.

Korg ksc files are just text files, so they're fairly easy to identify. The
output KSC file may occasionally have some junk data if it was partially
overwritten after delete, but they can be editted in a text editor.

$> korgfiles extract <diskimage> ksc

[Korg KMP files]

These files are key maps for mapping KSF data to keys.

Korg kmp files are the hardest to retrieve since they have no size info. The
tool just does its best to identify the end of the KMP file but it may
occasionally have junk at the end. These files typically aren't very useful
anyway because they depend on fixed ksf filenames which this tool cannot retrieve.

$> korgfiles extract <diskimage> kmp


------------------------------------------------------------------
|                          KSF2WAV                               |
------------------------------------------------------------------

$> korgfiles ksf2wav -h
usage: korgfiles ksf2wav [-h] [-keepname] ksffile [ksffile ...]

positional arguments:
  ksffile     ksf sound file(s) to convert to wav(s)

optional arguments:
  -h, --help  show this help message and exit
  -keepname   keep the ksf filename as the wav filename


Convert one of more KSF (Korg Sound File) files to WAV format. You can pass
a single file or use a wildcard to convert whole sets of ksf files. The
default wav filename is extracted from the KSF file itself. However, if
you use the -keepname option, the wav files will use the same names as the
input ksg files (but with the extension as .WAV instead of .KSF).
