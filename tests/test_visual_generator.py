# -*- coding: utf-8 -*-
import pytest
import os
import sys
import shutil
import unittest.mock as mock
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGNER_TOOLS = os.path.abspath(os.path.join(HERE, "..", "_company", "_agents", "designer", "tools"))
YOUTUBE_TOOLS = os.path.abspath(os.path.join(HERE, "..", "_company", "_agents", "youtube", "tools"))

if DESIGNER_TOOLS not in sys.path:
    sys.path.append(DESIGNER_TOOLS)
if YOUTUBE_TOOLS not in sys.path:
    sys.path.append(YOUTUBE_TOOLS)

import visual_director
import telegram_bot

def test_get_premium_font_fallback():
    """Verify that get_premium_font returns a valid font and falls back gracefully."""
    font = visual_director.get_premium_font(24, is_bold=False)
    assert font is not None
    
    font_bold = visual_director.get_premium_font(32, is_bold=True)
    assert font_bold is not None

def test_wrap_text_logic():
    """Test text wrapping helper functions for different line widths."""
    font = visual_director.get_premium_font(24)
    text = "This is a very long headline to test that our procedural text wrap wraps correctly"
    lines = visual_director.wrap_text(text, font, 200)
    assert len(lines) > 1
    assert " ".join(lines) == text

def test_draw_gradient_background():
    """Verify that draw_gradient_background generates an image of exact size."""
    img = visual_director.draw_gradient_background(1280, 720)
    assert img.size == (1280, 720)
    assert img.mode == "RGBA"

def test_generate_images_and_verify_dimensions(tmp_path):
    """Verify image generation writes files with exact expected dimensions."""
    # Temporarily override visual_director.GUIDES_DIR to a temporary folder
    original_guides_dir = visual_director.GUIDES_DIR
    temp_guides_dir = str(tmp_path / "visual_guides")
    visual_director.GUIDES_DIR = temp_guides_dir
    os.makedirs(temp_guides_dir, exist_ok=True)
    
    try:
        timestamp = "99991231_2359"
        main_title = '테스트 "로컬 AI" 1인 기업과 무결성'
        sub_title = "Pydantic v2와 E2E 121개 그린 테스트"
        
        # Mock Telegram dispatch to avoid network requests during test
        with mock.patch("visual_director._api_send_photos_to_telegram") as mock_send:
            visual_director.generate_images(timestamp, main_title, sub_title)
            
            # Assert file creation
            thumb_path = os.path.join(temp_guides_dir, f"thumbnail_{timestamp}.png")
            card_path = os.path.join(temp_guides_dir, f"card_news_{timestamp}.png")
            
            assert os.path.exists(thumb_path)
            assert os.path.exists(card_path)
            
            # Verify thumbnail dimensions
            with Image.open(thumb_path) as thumb_img:
                assert thumb_img.size == (1280, 720)
                
            # Verify card news dimensions
            with Image.open(card_path) as card_img:
                assert card_img.size == (1080, 1080)
                
            mock_send.assert_called_once_with(thumb_path, card_path)
    finally:
        visual_director.GUIDES_DIR = original_guides_dir

def test_telegram_bot_get_latest_visual_assets():
    """Verify get_latest_visual_assets correctly retrieves the latest generated PNG paths."""
    mock_files = ["thumbnail_20260526_1200.png", "card_news_20260526_1200.png"]
    
    def mock_exists(path):
        if path.endswith("visual_guides"):
            return True
        return os.path.exists(path)
        
    def mock_listdir(path):
        if path.endswith("visual_guides"):
            return mock_files
        return os.listdir(path)
        
    def mock_getmtime(path):
        return 1716768000.0  # Constant timestamp

    with mock.patch("os.path.exists", side_effect=mock_exists), \
         mock.patch("os.listdir", side_effect=mock_listdir), \
         mock.patch("os.path.getmtime", side_effect=mock_getmtime):
         
        latest_thumb, latest_card = telegram_bot.get_latest_visual_assets()
        assert latest_thumb is not None
        assert latest_card is not None
        assert "thumbnail_20260526_1200.png" in latest_thumb
        assert "card_news_20260526_1200.png" in latest_card

def test_telegram_bot_send_photo():
    """Verify telegram_bot.send_photo formats the request correctly and uploads multipart form data."""
    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    
    # Create a small dummy file to send
    dummy_file = "test_dummy_photo.png"
    with open(dummy_file, "wb") as f:
        f.write(b"mock_png_binary_data")
        
    try:
        with mock.patch("requests.post", return_value=mock_resp) as mock_post:
            success = telegram_bot.send_photo("mock_token", "mock_chat_id", dummy_file, "Cyberpunk Glow Theme")
            
            assert success is True
            mock_post.assert_called_once()
            called_args, called_kwargs = mock_post.call_args
            assert "mock_token" in called_args[0]
            assert called_kwargs["data"]["chat_id"] == "mock_chat_id"
            assert called_kwargs["data"]["caption"] == "Cyberpunk Glow Theme"
            assert "photo" in called_kwargs["files"]
    finally:
        if os.path.exists(dummy_file):
            os.remove(dummy_file)

def test_visual_director_telegram_dispatch_fallback():
    """Verify that visual_director's _api_send_photos_to_telegram handles missing or corrupt credentials gracefully."""
    # Ensure no exceptions are thrown when the credentials json is missing or invalid
    with mock.patch("os.path.exists", return_value=False):
        try:
            visual_director._api_send_photos_to_telegram("dummy_thumb.png", "dummy_card.png")
        except Exception as e:
            pytest.fail(f"_api_send_photos_to_telegram raised exception on missing credentials: {e}")
