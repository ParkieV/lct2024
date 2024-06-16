const path = require("path");

module.exports = {
    resolve: {
        extensions: ['.js', '.jsx']
    },
    entry: "./src/index.js",
    mode: "development",
    output: {
        path: path.resolve(__dirname, "build"),
        filename: "main.bundle.js",
        clean: {
            keep(asset) {
                return 'index.html' || '';
            }
        }
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: "babel-loader",
                }
            },
            {
                test: /\.css$/,
                use: [
                    "style-loader",
                    {
                        loader: "css-loader",
                        options: {
                            modules: true,
                        }
                    }
                ]
            }, {
                test: /\.(png|jpg|jpeg|gif|svg|webp)$/i,
                use: [
                    {
                        loader: 'file-loader',
                    },
                ],
            }
        ]
    },
    devServer: {
        static: {
            directory: path.join(__dirname, "build"),
        },
        compress: true,
        port: 9002
    }
}