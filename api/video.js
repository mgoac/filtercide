const scrape = require('@kaviaann/scrape');

module.exports = async (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');

  const videoUrl = req.query.url;
  if (!videoUrl) {
    return res.status(400).json({ error: 'Missing URL parameter' });
  }

  try {
    // Use the library to download the video info
    const result = await scrape.youtube(videoUrl);

    if (!result || !result.url) {
      throw new Error('No video URL found');
    }

    // Return the video URL as JSON
    res.status(200).json({
      success: true,
      videoUrl: result.url,
      title: result.title || 'Video',
      thumbnail: result.thumbnail || ''
    });
  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).json({ error: error.message });
  }
};