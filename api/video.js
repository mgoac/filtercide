const ytdl = require('ytdl-core');

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
    // Get video info with cookies and timeout
    const info = await Promise.race([
      ytdl.getInfo(videoUrl, {
        requestOptions: {
          headers: {
            Cookie: cookieString
          }
        }
      }),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 15000))
    ]);

    // Get the highest quality video + audio format
    const format = ytdl.chooseFormat(info.formats, { quality: 'highest' });

    // Return the video URL as JSON
    res.status(200).json({
      success: true,
      videoUrl: format.url,
      title: info.videoDetails.title,
      thumbnail: info.videoDetails.thumbnails[0].url
    });
  } catch (error) {
    console.error('Error:', error.message);
    res.status(500).json({ error: error.message });
  }
};