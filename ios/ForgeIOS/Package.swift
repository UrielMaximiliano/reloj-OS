// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ForgeIOS",
    platforms: [
        .iOS(.v16)
    ],
    products: [
        .library(
            name: "ForgeIOS",
            targets: ["ForgeIOS"]
        )
    ],
    targets: [
        .target(
            name: "ForgeIOS",
            path: "Sources/ForgeIOS"
        )
    ]
)
