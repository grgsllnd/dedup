Overall, you’ve got the core logic in place, but here are a few things I’d double‑check or enhance before you call it “done”:
	0. Modularize code
    1.	Excluding found_duplicates everywhere
You added a skip for any root path under found_duplicates, which is great—but make sure that happens before you count files for progress and that it applies to both duplicate and unique passes. Otherwise you’ll mis‐count total and might accidentally try to re‑move something you just dropped into found_duplicates.
	2.	Null or missing destination
If the user hasn’t picked a destination (i.e. app_state.destination is None or empty), you quietly return—but you might want to show an error in the dialog (“Please select a destination first”) rather than doing nothing.
	3.	Threading / UI responsiveness
Right now you run all of this in __init__, blocking the Qt event loop. For any non‑trivial folder tree that can take seconds or minutes, the dialog will freeze. I’d recommend moving the merge into a worker thread or at least kicking it off from a “Start” button instead of auto‑running in the constructor.
	4.	Updating the checksum index
You index the destination once up front. But after you move a unique file into the destination you don’t add its checksum to dest_checksums. That means if two sources have the same new file, you’ll move the first and then you’ll wrongly treat the second as “unique” and overwrite it. To prevent that, either append new checksums to your in‑memory map or re‑run write_destination_list() after each move (at the cost of performance).
	5.	Memory usage on large files
You’re currently doing open(path, "rb").read() for each hash, which will buffer the entire file in memory. For huge files you’d be safer reading in chunks (e.g. by passing the file handle into xxhash in 8 KB blocks), just like your MD5 helper did earlier.
	6.	Overwrite protection vs. skipping
You skip moving a unique file if a same‑name file already exists in that subfolder of the destination—but you leave it in the source. That’s fine, but you may want to log why you skipped (e.g. name clash vs. checksum match) so the user can resolve it manually.
	7.	Indentation bug in the snippet
Make sure your for name in files: loop is properly nested under the for root, _, files in os.walk(...) and that your if "found_duplicates" check lives at the same level. A misplaced indent could mean you never enter the file loop.
	8.	Feedback to the user
Consider adding a “Cancel” button on the dialog, or at least disabling “Close” until the merge is complete, so they don’t accidentally dismiss halfway through.

If you cover those, you’ll have a robust, user‑friendly “merge sources into destination” feature!