"use strict";

(async () => {
  const root = document.getElementById("blogposts");

  const posts = await window
    .fetch(
      "https://blog.zekro.de/ghost/api/v3/content/posts/?key=ca573b41d238f5f6db2e26d1d5&limit=4&fields=title,url,excerpt,feature_image"
    )
    .then((res) => res.json());

  for (const post of posts.posts) {
    const container = document.createElement("a");
    container.href = post.url;
    container.target = "_blank";

    const img = document.createElement("div");
    img.style.backgroundImage = `url(${post.feature_image})`;
    container.appendChild(img);

    const header = document.createElement("h3");
    header.innerText = post.title;
    container.appendChild(header);

    const excerpt = document.createElement("p");
    excerpt.innerText = post.excerpt.split(" ").slice(0, 30).join(" ") + " ...";
    container.appendChild(excerpt);

    root.appendChild(container);
  }
})();
