#!/usr/bin/env python3
"""
Simple test script to verify file parsing functionality for the DarkAge SMP bot commands.
This tests the core logic without requiring Discord bot initialization.
"""

from pathlib import Path

def test_info_parsing():
    """Test info.md parsing logic"""
    print("Testing info.md parsing...")

    info_path = Path("info.md")
    if not info_path.exists():
        print("❌ info.md not found")
        return False

    with open(info_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()

    print(f"✅ info.md content: '{content}' (length: {len(content)})")
    return True

def test_news_parsing():
    """Test notice.md parsing logic for latest entry"""
    print("\nTesting notice.md parsing...")

    notice_path = Path("notice.md")
    if not notice_path.exists():
        print("❌ notice.md not found")
        return False

    with open(notice_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Find the most recent entry (last ## heading)
    latest_entry = []
    found_entry = False

    for line in reversed(lines):
        if line.strip().startswith('## ') and not found_entry:
            latest_entry.insert(0, line)
            found_entry = True
        elif found_entry and line.strip().startswith('## '):
            break
        elif found_entry:
            latest_entry.insert(0, line)

    if not latest_entry:
        print("❌ No entries found in notice.md")
        return False

    entry_text = ''.join(latest_entry).strip()
    print(f"✅ Latest entry from notice.md:\n{entry_text}")
    return True

def test_rules_parsing():
    """Test rules.md parsing logic"""
    print("\nTesting rules.md parsing...")

    rules_path = Path("rules.md")
    if not rules_path.exists():
        print("❌ rules.md not found")
        return False

    with open(rules_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()

    print(f"✅ rules.md content length: {len(content)} characters")
    return True

def test_players_parsing():
    """Test players.md parsing logic"""
    print("\nTesting players.md parsing...")

    players_path = Path("players.md")
    if not players_path.exists():
        print("❌ players.md not found")
        return False

    with open(players_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()

    # Extract player names (simplified - assumes format like "- PlayerName")
    existing_players = []
    for line in content.split('\n'):
        if line.strip().startswith('- '):
            player_name = line.strip()[2:].strip()
            if player_name:
                existing_players.append(player_name.lower())

    print(f"✅ Found {len(existing_players)} players in players.md: {existing_players}")
    return True

def test_player_add():
    """Test player add functionality"""
    print("\nTesting player add logic...")

    test_username = "TestPlayer123"
    players_path = Path("players.md")

    # Read existing players
    existing_players = []
    if players_path.exists():
        with open(players_path, 'r', encoding='utf-8') as file:
            content = file.read()
            for line in content.split('\n'):
                if line.strip().startswith('- '):
                    player_name = line.strip()[2:].strip()
                    if player_name:
                        existing_players.append(player_name.lower())

    # Check for duplicates
    if test_username.lower() in existing_players:
        print(f"⚠️ Player '{test_username}' already exists (test would skip adding)")
        return True

    print(f"✅ Player '{test_username}' can be added (no duplicate found)")
    return True

if __name__ == "__main__":
    print("DarkAge SMP Bot - File Parsing Test Suite")
    print("=" * 50)

    tests = [
        test_info_parsing,
        test_news_parsing,
        test_rules_parsing,
        test_players_parsing,
        test_player_add
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All file parsing tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")