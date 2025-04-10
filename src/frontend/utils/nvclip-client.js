// src/frontend/utils/nvclip-client.js
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

async function queryNVClip(imageBase64, text) {
  const response = await fetch("http://localhost:11434/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "nvclip",
      messages: [
        {
          role: "user",
          content: text,
          images: [imageBase64]
        }
      ]
    }),
  });

  const data = await response.json();
  return data.message.content;
}

// Export the function for use in other components
module.exports = { queryNVClip };