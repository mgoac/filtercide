const axios = require('axios');
const cheerio = require('cheerio');

module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');

  const videoUrl = req.query.url;
  if (!videoUrl) {
    return res.status(400).json({ error: 'Missing URL parameter' });
  }

  // Parse cookies from environment variable
  let cookies = [];
  try {
    cookies = JSON.parse(process.env.YT_COOKIES || '[]');
  } catch {
    return res.status(500).json({ error: 'Invalid cookie format' });
  }

  // Build cookie string
  const cookieString = cookies.map(c => `${c.name}=${c.value}`).join('; ');

  try {
    // Fetch the YouTube page
    const response = await axios.get(videoUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': cookieString
      },
      timeout: 15000
    });

    const html = response.data;
    const $ = cheerio.load(html);

    // Extract video title
    const title = $('meta[name="title"]').attr('content') || $('h1.ytd-video-primary-info-renderer').text().trim() || 'Video';

    // Extract thumbnail
    const thumbnail = $('meta[property="og:image"]').attr('content') || '';

    // Extract video URL from player response
    const playerResponseMatch = html.match(/ytInitialPlayerResponse\s*=\s*({.*?});/);
    if (!playerResponseMatch) {
      throw new Error('Could not find player response in page');
    }

    const playerResponse = JSON.parse(playerResponseMatch[1]);
    const formats = playerResponse?.streamingData?.formats || [];
    const adaptiveFormats = playerResponse?.streamingData?.adaptiveFormats || [];
    const allFormats = [...formats, ...adaptiveFormats];

    // Find the best video+audio format
    const bestFormat = allFormats
      .filter(f => f.mimeType && f.mimeType.includes('mp4'))
      .sort((a, b) => (b.bitrate || 0) - (a.bitrate || 0))[0];

    if (!bestFormat || !bestFormat.url) {
      throw new Error('No video URL found');
    }

    // Return the video URL as JSON
    res.status(200).json({
      success: true,
      videoUrl: bestFormat.url,
      title: title,
      thumbnail: thumbnail
    });
  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).json({ error: error.message });
  }
};