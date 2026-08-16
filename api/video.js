const ytdl = require('ytdl-core');

module.exports = async (req, res) => {
  const videoUrl = req.query.url;
  if (!videoUrl) return res.status(400).send('Missing URL');

  // Parse cookies from environment variable
  let cookies = [];
  try {
    cookies = JSON.parse(process.env.YT_COOKIES || '[]');
  } catch {
    return res.status(500).send('Invalid cookie format');
  }

  try {
    const info = await ytdl.getInfo(videoUrl, {
      requestOptions: {
        headers: {
          Cookie: cookies.map(c => `${c.name}=${c.value}`).join('; ')
        }
      }
    });

    const format = ytdl.chooseFormat(info.formats, { quality: 'highestvideo' });
    res.redirect(format.url);
  } catch (err) {
    res.status(500).send(err.message);
  }
};