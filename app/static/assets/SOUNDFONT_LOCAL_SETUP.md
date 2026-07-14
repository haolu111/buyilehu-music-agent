# Local SoundFont Assets

国内部署时不要依赖 GitHub、jsDelivr 或 Hugging Face 直连。请把前端真实采样音色资源预缓存到本机服务器。

推荐目录：

```text
app/static/assets/
  soundfont-player/
    soundfont-player.js
  midi-js-soundfonts/
    FluidR3_GM/
      acoustic_grand_piano-mp3.js
      violin-mp3.js
      flute-mp3.js
      koto-mp3.js
      acoustic_guitar_nylon-mp3.js
      cello-mp3.js
      clarinet-mp3.js
      xylophone-mp3.js
```

也可以放到运行时目录，生产环境更推荐：

```text
.music-agent-runtime/assets/
  soundfont-player/soundfont-player.js
  midi-js-soundfonts/FluidR3_GM/*.js
```

运行后浏览器会按这个顺序加载：

1. `/runtime-assets/soundfont-player/soundfont-player.js`
2. `/static/assets/soundfont-player/soundfont-player.js`
3. `/runtime-assets/midi-js-soundfonts/FluidR3_GM/<instrument>-mp3.js`
4. `/static/assets/midi-js-soundfonts/FluidR3_GM/<instrument>-mp3.js`
5. 外部镜像/CDN 兜底

如果本地音色不存在，页面仍会尝试外部地址，最后才降级到 Web Audio 合成音。
