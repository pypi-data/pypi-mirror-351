# stoken_bfasst: SecurID Token BruteForce Assistant

## Why

Consider the following.

You lost the original "sdtid" file that contains your RSA SecurID soft token file, and for whatever reason the tokencode generator program doesn't implement a way to export it back to a sdtid file. However, you can easily create a memory dump of the program while it has your soft token loaded in memory. How can you quickly search through that memory dump to find your secret seed and rebuild a sdtid file (which you will definitely back up properly this time)?

This library lets you do that.

## How to use

I am tired so there are no proper docs. Read `tests/test_search.py` and the public function docstrings.

Sorry.
