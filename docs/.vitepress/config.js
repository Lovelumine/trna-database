// docs/.vitepress/config.js
export default {
    title: '帮助文档',
    description: '这是一个帮助文档页面',
    themeConfig: {
      nav: [
        { text: '首页', link: '/' },
        { text: '指南', link: '/guide/' },
      ],
      sidebar: {
        '/guide/': [
          {
            text: '指南',
            children: [
              { text: '介绍', link: '/guide/' },
              { text: '快速开始', link: '/guide/quickstart' },
            ],
          },
        ],
      },
    },
  }
  