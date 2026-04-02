# 人生の旅マップ

引越し遍歴を 3D マップで 120 秒かけて紹介する、Next.js 製の自己紹介サイトです。  
MapLibre GL JS で全画面マップを表示し、大村から奥沢まで 9 拠点を自動飛行します。

## ローカル起動

```bash
npm install
cp .env.example .env.local
npm run dev
```

`http://localhost:3000` を開くと、中央の「人生の旅をスタート」ボタンから旅を再生できます。

## 技術構成

- Next.js 16 App Router
- React 19
- Tailwind CSS 4
- MapLibre GL JS
- MapTiler Maps API

## MapTiler キー

地図スタイルは `NEXT_PUBLIC_MAPTILER_API_KEY` を使って MapTiler から読み込みます。  
ローカル開発では `.env.local`、GitHub Actions では Secret、Railway では同名の環境変数を設定してください。

## Railway デプロイ

このアプリは `life-journey-map/` 配下だけで完結する isolated monorepo 想定です。

### 方法 1: Railway の root directory を使う

- Railway の対象サービスで Root Directory を `life-journey-map` に設定
- Build / Start は `railway.toml` をそのまま利用

### 方法 2: JavaScript monorepo として自動検出させる

- このリポジトリをそのまま Railway に接続
- `life-journey-map` を deployable package として選ぶ

### GitHub push で自動デプロイする

`.github/workflows/railway-deploy-life-journey-map.yml` を追加してあります。  
`main` へ push され、かつ `life-journey-map/` 配下に変更があると、GitHub Actions から Railway CLI でデプロイします。

必要な GitHub Secrets:

- `RAILWAY_TOKEN`
  Railway の Project Token を推奨
- `RAILWAY_PROJECT_ID`
  Railway のプロジェクト ID
- `RAILWAY_ENVIRONMENT_NAME`
  例: `production`
- `RAILWAY_SERVICE_NAME`
  対象サービス名
- `NEXT_PUBLIC_MAPTILER_API_KEY`
  MapTiler のブラウザ公開用 API キー

補足:

- workflow 内で `npm run lint` と `npm run build` が成功した場合だけデプロイします
- Railway 側の service variables にも `NEXT_PUBLIC_MAPTILER_API_KEY` を設定してください
- Railway 側で GitHub 連携の `Wait for CI` を有効にすると、GitHub Actions 成功後に Railway の GitHub autodeploy を待たせる構成にもできます

## GitHub Pages 公開

静的公開用 workflow は `.github/workflows/deploy-life-journey-map-pages.yml` に追加してあります。  
`main` に push され、`life-journey-map/` に変更があると GitHub Pages に再デプロイされます。

前提:

- GitHub repository settings で Pages を `GitHub Actions` ソースに設定
- Repository Secret に `NEXT_PUBLIC_MAPTILER_API_KEY` を登録

公開 URL は project pages の場合、`https://<owner>.github.io/estimate-backend-calc/` です。

## 補足

- 3D 建物は OpenFreeMap のベクタータイルを利用
- 最終地点の奥沢では 360 度 Orbit して停止
