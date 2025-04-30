def write_destination_list(self):
        from settings.state import app_state
        dest = app_state.destination
        if not dest:
            return
        checksums = {}
        for root, _, filenames in os.walk(dest):
            for f in filenames:
                path = os.path.join(root, f)
                h = xxhash.xxh64_hexdigest(open(path, "rb").read())
                checksums.setdefault(h, []).append(path)
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(data_dir / "destination_files.json", "w", encoding="utf-8") as jf:
            json.dump(checksums, jf, indent=2)