const path = require('path');

module.exports = {
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(woff|woff2|ttf|eot)$/,
        use: 'file-loader?name=./static/frontend/fonts/[name].[ext]!static'
      },
      {
        test: /\.(png|jpe?g|gif)$/i,
        use: [
          {
            loader: 'file-loader?name=./static/frontend/img/[name].[ext]',
          },
        ],
      }
    ]
  },
  entry: {
    main: './src/index.js',
    auth: './src/auth.js'
  },
  output: {
    filename: './static/frontend/[name].js',
    path: path.resolve(__dirname)
  },
  devServer: {
    writeToDisk: true, // Write files to disk in dev mode, so Django can serve the assets
  },
};
