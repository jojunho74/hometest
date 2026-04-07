export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  const { query, type = 'blog' } = req.query;
  if (!query) return res.status(400).json({ error: 'query required' });

  const clientId     = process.env.NAVER_CLIENT_ID;
  const clientSecret = process.env.NAVER_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    return res.status(500).json({ error: 'NAVER API keys not configured' });
  }

  const validTypes = ['blog', 'news'];
  const searchType = validTypes.includes(type) ? type : 'blog';
  const url = `https://openapi.naver.com/v1/search/${searchType}?query=${encodeURIComponent(query)}&display=5&sort=date`;

  try {
    const response = await fetch(url, {
      headers: {
        'X-Naver-Client-Id':     clientId,
        'X-Naver-Client-Secret': clientSecret,
      }
    });
    const data = await response.json();
    res.status(200).json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}
