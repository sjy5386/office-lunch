#!/bin/sh

set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
RUN_NOW=0
MODE="install"
OUTPUT_DIR=""

usage() {
	echo "Usage: $0 [--run-now] [--write-dir PATH]" >&2
	exit 2
}

template_paths() {
	/usr/bin/find "$SCRIPT_DIR" -maxdepth 1 -type f -name 'com.office-lunch.*.plist.template' | /usr/bin/sort
}

render_template() {
	TEMPLATE_PATH="$1"
	/usr/bin/sed \
		-e "s|__LABEL__|$LABEL|g" \
		-e "s|__DOCKER_BIN__|$DOCKER_BIN|g" \
		-e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
		-e "s|__HOME_DIR__|$HOME|g" \
		"$TEMPLATE_PATH"
}

install_template() {
	TEMPLATE_PATH="$1"
	LABEL="$(basename "$TEMPLATE_PATH" .plist.template)"
	TARGET_PATH="$HOME/Library/LaunchAgents/$LABEL.plist"

	render_template "$TEMPLATE_PATH" > "$TARGET_PATH"
	/usr/bin/plutil -lint "$TARGET_PATH" >/dev/null

	if /bin/launchctl print "gui/$(/usr/bin/id -u)/$LABEL" >/dev/null 2>&1; then
		/bin/launchctl bootout "gui/$(/usr/bin/id -u)" "$TARGET_PATH" >/dev/null 2>&1 || true
	fi

	/bin/launchctl bootstrap "gui/$(/usr/bin/id -u)" "$TARGET_PATH"

	if [ "$RUN_NOW" -eq 1 ]; then
		/bin/launchctl kickstart -k "gui/$(/usr/bin/id -u)/$LABEL"
	fi

	echo "Installed $TARGET_PATH"
}

write_template() {
	TEMPLATE_PATH="$1"
	LABEL="$(basename "$TEMPLATE_PATH" .plist.template)"
	TARGET_PATH="$OUTPUT_DIR/$LABEL.plist"

	render_template "$TEMPLATE_PATH" > "$TARGET_PATH"
	/usr/bin/plutil -lint "$TARGET_PATH" >/dev/null
	echo "Wrote $TARGET_PATH"
}

while [ "$#" -gt 0 ]; do
	case "$1" in
		--run-now)
			RUN_NOW=1
			;;
		--write-dir)
			shift
			[ "$#" -gt 0 ] || usage
			MODE="write-dir"
			OUTPUT_DIR="$1"
			;;
		*)
			usage
			;;
	esac
	shift
done

if ! DOCKER_BIN="$(command -v docker)"; then
	echo "docker executable not found in PATH" >&2
	exit 1
fi

if ! template_paths | /usr/bin/grep . >/dev/null; then
	echo "No plist templates found in $SCRIPT_DIR" >&2
	exit 1
fi

case "$MODE" in
	write-dir)
		/bin/mkdir -p "$OUTPUT_DIR"
		template_paths | while IFS= read -r TEMPLATE_PATH; do
			write_template "$TEMPLATE_PATH"
		done
		exit 0
		;;
esac

/bin/mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
template_paths | while IFS= read -r TEMPLATE_PATH; do
	install_template "$TEMPLATE_PATH"
done
