# -*- coding: utf-8 -*-
import pytest
import os
import sys
import unittest.mock as mock

HERE = os.path.dirname(os.path.abspath(__file__))
EDITOR_TOOLS = os.path.abspath(os.path.join(HERE, "..", "_company", "_agents", "editor", "tools"))
YOUTUBE_TOOLS = os.path.abspath(os.path.join(HERE, "..", "_company", "_agents", "youtube", "tools"))

if EDITOR_TOOLS not in sys.path:
    sys.path.append(EDITOR_TOOLS)
if YOUTUBE_TOOLS not in sys.path:
    sys.path.append(YOUTUBE_TOOLS)

import music_generate
import telegram_bot

def test_extract_mood_from_latest_post_fallback():
    """Verify that extract_mood_from_latest_post returns default value if directory does not exist."""
    with mock.patch("os.path.exists", return_value=False):
        mood = music_generate.extract_mood_from_latest_post()
        assert "hopeful tech theme" in mood

def test_extract_mood_from_latest_post_keywords(tmp_path):
    """Verify keyword extraction matches content keywords like '보안' or '가드레일'."""
    original_workspace = music_generate.WORKSPACE
    # Point workspace to a temp directory structure
    music_generate.WORKSPACE = str(tmp_path)
    
    posts_dir = os.path.join(tmp_path, "_company", "_agents", "youtube", "tools", "naver_posts")
    os.makedirs(posts_dir, exist_ok=True)
    
    post_file = os.path.join(posts_dir, "post_1.md")
    with open(post_file, "w", encoding="utf-8") as f:
        f.write("이것은 보안 가드레일에 대한 기업 마케팅 글입니다.")
        
    try:
        mood = music_generate.extract_mood_from_latest_post()
        # Since '보안' matches cybersecurity mood: "cybersecurity dark ambient electronic"
        assert "cybersecurity" in mood
    finally:
        music_generate.WORKSPACE = original_workspace

def test_generate_simulated(tmp_path):
    """Verify simulated generator produces a valid mock MP3 file with precise signature bytes."""
    output_path = os.path.join(tmp_path, "test_bgm.mp3")
    ok, result = music_generate._generate_simulated("cyberpunk style", 10, output_path)
    
    assert ok is True
    assert result == output_path
    assert os.path.exists(output_path)
    
    with open(output_path, "rb") as f:
        data = f.read()
        assert data.startswith(b"\xFF\xFB\x90\x44")
        assert b"TAGCONNECT_AI_MOCK_BGM_LUNA_COMPLIANT" in data

def test_api_send_audio_to_telegram_fallback():
    """Verify _api_send_audio_to_telegram handles invalid/missing credentials gracefully."""
    with mock.patch("os.path.exists", return_value=False):
        success = music_generate._api_send_audio_to_telegram("dummy_path.mp3", "hopeful tech theme")
        assert success is False

def test_telegram_bot_get_latest_bgm_assets():
    """Verify get_latest_bgm_assets resolves path and finds the latest MP3 file."""
    mock_files = ["bgm_20260526_120000.mp3", "bgm_20260526_130000.mp3"]
    
    def mock_exists(path):
        if "connect-ai-music" in path:
            return True
        return os.path.exists(path)
        
    def mock_listdir(path):
        if "connect-ai-music" in path:
            return mock_files
        return os.listdir(path)
        
    def mock_getmtime(path):
        if "120000" in path:
            return 1716768000.0
        return 1716771600.0 # Later timestamp

    with mock.patch("os.path.exists", side_effect=mock_exists), \
         mock.patch("os.listdir", side_effect=mock_listdir), \
         mock.patch("os.path.getmtime", side_effect=mock_getmtime):
         
        latest = telegram_bot.get_latest_bgm_assets()
        assert latest is not None
        assert "bgm_20260526_130000.mp3" in latest

def test_telegram_bot_send_audio(tmp_path):
    """Verify send_audio correctly constructs multipart post request."""
    dummy_file = os.path.join(tmp_path, "dummy.mp3")
    with open(dummy_file, "wb") as f:
        f.write(b"dummy_mp3_data")
        
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    
    with mock.patch("requests.post", return_value=mock_resp) as mock_post:
        success = telegram_bot.send_audio("mock_token", "mock_chat_id", dummy_file, "Premium procedural BGM")
        
        assert success is True
        mock_post.assert_called_once()
        called_args, called_kwargs = mock_post.call_args
        assert "mock_token" in called_args[0]
        assert called_kwargs["data"]["chat_id"] == "mock_chat_id"
        assert called_kwargs["data"]["caption"] == "Premium procedural BGM"
        assert "audio" in called_kwargs["files"]

def test_sound_generator_double_sending_prevention():
    """Verify that music_generate does not send audio to Telegram when CAMP_ORCHESTRATOR_RUNNING is set to '1'."""
    with mock.patch.dict(os.environ, {"CAMP_ORCHESTRATOR_RUNNING": "1"}), \
         mock.patch("music_generate._api_send_audio_to_telegram") as mock_send:
         
        mock_setup = {"INSTALLED_MODEL": "Simulated BGM Engine"}
        mock_gen_cfg = {"PROMPT": "test", "DURATION_SEC": 5, "OUTPUT_DIR": "dummy_out"}
        
        def mock_load(p):
            if "setup" in p: return mock_setup
            return mock_gen_cfg
            
        with mock.patch("music_generate._load", side_effect=mock_load), \
             mock.patch("music_generate._generate_simulated", return_value=(True, "dummy_out/bgm_test.mp3")), \
             mock.patch("os.path.getsize", return_value=100), \
             mock.patch("builtins.open", mock.mock_open()):
             
            music_generate.main()
            
            # Assert that the individual _api_send_audio_to_telegram was NOT called
            mock_send.assert_not_called()

