# launchd setup

macOS `launchd` + `docker compose`로 식단 수집을 자동 실행하는 설정 문서다.

## 동작 방식

`launchd`가 정해진 시간에 `docker compose run --rm app`을 실행한다.  
실행 시점마다 각 잡이 `MENU_FREQUENCY`를 직접 주입하고, 나머지 설정은 프로젝트 루트의 `.env`에서 읽는다.

생성되는 잡은 3개다.

- `com.office-lunch.weekly`: 월요일 11:10, `MENU_FREQUENCY=WEEKLY`
- `com.office-lunch.daily-lunch`: 월-금 11:15, `MENU_FREQUENCY=DAILY_LUNCH`
- `com.office-lunch.daily-dinner`: 월-금 17:30, `MENU_FREQUENCY=DAILY_DINNER`

시간 해석은 macOS 로컬 시간대를 따른다.

## 준비물

- macOS
- `docker compose`가 동작하는 Docker 환경
- Slack 전송에 사용할 값
  - `SLACK_BOT_TOKEN`
  - `SLACK_CHANNEL_ID`

## 설정

프로젝트 루트에서 `.env` 파일을 만든다.

```bash
PROJECT_DIR=/path/to/office-lunch
cd "$PROJECT_DIR"
cp .env.example .env
```

필수 값:

```dotenv
SLACK_BOT_TOKEN=...
SLACK_CHANNEL_ID=...
```

선택 값:

```dotenv
# 특정 식당 하나만 보내고 싶을 때만 설정
RESTAURANT=알찬푸드_구내식당
```

`RESTAURANT`를 쓰면 `MENU_FREQUENCY`로 고른 대상 대신 해당 enum 이름 하나만 실행한다. 값은 `restaurant.py`의 `Restaurant` enum 이름과 정확히 일치해야 한다.

## 설치

프로젝트 루트에서 아래 스크립트를 실행하면 `~/Library/LaunchAgents`에 실제 plist 3개를 생성하고 등록한다.

```bash
PROJECT_DIR=/path/to/office-lunch
cd "$PROJECT_DIR"
./launchd/install-launch-agent.sh
```

즉시 한 번씩 실행까지 하려면:

```bash
PROJECT_DIR=/path/to/office-lunch
cd "$PROJECT_DIR"
./launchd/install-launch-agent.sh --run-now
```

주의:

- `--run-now`는 3개 잡을 모두 바로 한 번씩 실행한다.
- 스크립트를 다시 실행하면 기존 잡을 덮어써서 갱신한다.

## 설치 결과

등록 후 아래 파일들이 생긴다.

- `~/Library/LaunchAgents/com.office-lunch.weekly.plist`
- `~/Library/LaunchAgents/com.office-lunch.daily-lunch.plist`
- `~/Library/LaunchAgents/com.office-lunch.daily-dinner.plist`

로그는 아래에 남는다.

- `~/Library/Logs/office-lunch.weekly.stdout.log`
- `~/Library/Logs/office-lunch.weekly.stderr.log`
- `~/Library/Logs/office-lunch.daily-lunch.stdout.log`
- `~/Library/Logs/office-lunch.daily-lunch.stderr.log`
- `~/Library/Logs/office-lunch.daily-dinner.stdout.log`
- `~/Library/Logs/office-lunch.daily-dinner.stderr.log`

## 상태 확인

등록 여부 확인:

```bash
launchctl print gui/$(id -u)/com.office-lunch.weekly
launchctl print gui/$(id -u)/com.office-lunch.daily-lunch
launchctl print gui/$(id -u)/com.office-lunch.daily-dinner
```

로그 확인:

```bash
tail -f ~/Library/Logs/office-lunch.daily-lunch.stdout.log
tail -f ~/Library/Logs/office-lunch.daily-lunch.stderr.log
```

## 수동 실행

스케줄을 기다리지 않고 특정 유형만 한 번 실행하고 싶다면, 프로젝트 루트에서:

```bash
PROJECT_DIR=/path/to/office-lunch
cd "$PROJECT_DIR"
docker compose run --rm -e MENU_FREQUENCY=WEEKLY app
docker compose run --rm -e MENU_FREQUENCY=DAILY_LUNCH app
docker compose run --rm -e MENU_FREQUENCY=DAILY_DINNER app
```

## plist만 미리 생성해서 보기

설치하지 않고 렌더링 결과만 확인하려면, 프로젝트 루트에서:

```bash
PROJECT_DIR=/path/to/office-lunch
cd "$PROJECT_DIR"
./launchd/install-launch-agent.sh --write-dir /tmp/office-lunch-launchd
```

그러면 `/tmp/office-lunch-launchd` 아래에 실제 plist 3개가 생성된다.

## 제거

잡을 제거하려면:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.office-lunch.weekly.plist
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.office-lunch.daily-lunch.plist
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.office-lunch.daily-dinner.plist
rm ~/Library/LaunchAgents/com.office-lunch.weekly.plist
rm ~/Library/LaunchAgents/com.office-lunch.daily-lunch.plist
rm ~/Library/LaunchAgents/com.office-lunch.daily-dinner.plist
```
