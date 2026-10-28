#!/usr/bin/env swift
import AppKit
import Dispatch
import Foundation

struct Detection {
    let left: Int
    let top: Int
    let right: Int
    let bottom: Int
    let pixels: Int
}

func rgb(_ data: UnsafeMutablePointer<UInt8>, _ rowBytes: Int, _ pixelStride: Int, _ samples: Int, _ x: Int, _ y: Int) -> (Double, Double, Double) {
    let offset = y * rowBytes + x * pixelStride
    if samples >= 3 {
        if pixelStride >= 4 {
            return (Double(data[offset]), Double(data[offset + 1]), Double(data[offset + 2]))
        }
        return (Double(data[offset + 2]), Double(data[offset + 1]), Double(data[offset]))
    }
    let gray = Double(data[offset])
    return (gray, gray, gray)
}

func detectWatermark(_ rep: NSBitmapImageRep) -> Detection? {
    guard rep.bitsPerSample == 8, !rep.isPlanar, let pixels = rep.bitmapData else { return nil }
    let width = rep.pixelsWide
    let height = rep.pixelsHigh
    let pixelStride = rep.bytesPerRow / width
    let dimension = max(width, height)
    let scale = Double(dimension) / 480.0
    let roiWidth = min(width, Int(Double(dimension) * 0.20))
    let roiHeight = min(height, Int(Double(dimension) * 0.15))
    var count = 0
    var minX = width
    var maxX = 0
    var minY = height
    var maxY = 0

    for y in 0..<roiHeight {
        for x in 0..<roiWidth {
            let (red, green, blue) = rgb(pixels, rep.bytesPerRow, pixelStride, rep.samplesPerPixel, x, y)
            if red > 140 && red - green > 45 && red - blue > 45 {
                count += 1
                minX = min(minX, x)
                maxX = max(maxX, x)
                minY = min(minY, y)
                maxY = max(maxY, y)
            }
        }
    }

    guard count > Int(140 * scale * scale), minX < width, minY < height else { return nil }
    let xRatio = Double(minX) / Double(dimension)
    let yRatio = Double(minY) / Double(dimension)
    let widthRatio = Double(maxX - minX + 1) / Double(dimension)
    let heightRatio = Double(maxY - minY + 1) / Double(dimension)
    guard (0.005...0.05).contains(xRatio),
          (0.005...0.05).contains(yRatio),
          (0.05...0.19).contains(widthRatio),
          (0.04...0.17).contains(heightRatio) else { return nil }

    let margin = max(2, Int(Double(dimension) * 0.006))
    return Detection(
        left: max(1, minX - margin),
        top: max(1, minY - margin),
        right: min(width - 2, maxX + margin),
        bottom: min(height - 2, maxY + margin),
        pixels: count
    )
}

func repair(_ rep: NSBitmapImageRep, _ box: Detection) throws {
    guard let pixels = rep.bitmapData else { throw NSError(domain: "Watermark", code: 1) }
    let width = rep.pixelsWide
    let rowBytes = rep.bytesPerRow
    let pixelStride = rowBytes / width
    let samples = rep.samplesPerPixel
    let x0 = box.left
    let x1 = box.right
    let y0 = box.top
    let y1 = box.bottom

    let tl = rgb(pixels, rowBytes, pixelStride, samples, x0 - 1, y0 - 1)
    let tr = rgb(pixels, rowBytes, pixelStride, samples, x1 + 1, y0 - 1)
    let bl = rgb(pixels, rowBytes, pixelStride, samples, x0 - 1, y1 + 1)
    let br = rgb(pixels, rowBytes, pixelStride, samples, x1 + 1, y1 + 1)

    for y in y0...y1 {
        let v = Double(y - (y0 - 1)) / Double((y1 + 1) - (y0 - 1))
        for x in x0...x1 {
            let u = Double(x - (x0 - 1)) / Double((x1 + 1) - (x0 - 1))
            let left = rgb(pixels, rowBytes, pixelStride, samples, x0 - 1, y)
            let right = rgb(pixels, rowBytes, pixelStride, samples, x1 + 1, y)
            let top = rgb(pixels, rowBytes, pixelStride, samples, x, y0 - 1)
            let bottom = rgb(pixels, rowBytes, pixelStride, samples, x, y1 + 1)
            let channels = [0, 1, 2].map { channel -> UInt8 in
                let corners = [tl, tr, bl, br].map { value -> Double in
                    switch channel {
                    case 0: return value.0
                    case 1: return value.1
                    default: return value.2
                    }
                }
                let l = channel == 0 ? left.0 : (channel == 1 ? left.1 : left.2)
                let r = channel == 0 ? right.0 : (channel == 1 ? right.1 : right.2)
                let t = channel == 0 ? top.0 : (channel == 1 ? top.1 : top.2)
                let b = channel == 0 ? bottom.0 : (channel == 1 ? bottom.1 : bottom.2)
                let boundary = (1 - u) * l + u * r + (1 - v) * t + v * b
                let bilinear = (1 - u) * (1 - v) * corners[0]
                    + u * (1 - v) * corners[1]
                    + (1 - u) * v * corners[2]
                    + u * v * corners[3]
                return UInt8(max(0, min(255, (boundary - bilinear).rounded())))
            }
            let offset = y * rowBytes + x * pixelStride
            if pixelStride >= 4 {
                pixels[offset] = channels[0]
                pixels[offset + 1] = channels[1]
                pixels[offset + 2] = channels[2]
            } else {
                pixels[offset] = channels[2]
                pixels[offset + 1] = channels[1]
                pixels[offset + 2] = channels[0]
            }
        }
    }
}

func process(_ input: URL, _ outputBase: URL) throws -> (Detection?, URL) {
    let sourceData = try Data(contentsOf: input, options: .mappedIfSafe)
    guard let rep = NSBitmapImageRep(data: sourceData) else {
        throw NSError(domain: "Watermark", code: 2, userInfo: [NSLocalizedDescriptionKey: "Cannot decode \(input.path)"])
    }
    let detection = detectWatermark(rep)
    let outputExtension = detection == nil ? input.pathExtension.lowercased() : "jpg"
    let output = outputBase.appendingPathExtension(outputExtension.isEmpty ? "jpg" : outputExtension)
    try FileManager.default.createDirectory(at: output.deletingLastPathComponent(), withIntermediateDirectories: true)
    guard let box = detection else {
        try FileManager.default.copyItem(at: input, to: output)
        return (nil, output)
    }
    try repair(rep, box)
    guard let encoded = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.97]) else {
        throw NSError(domain: "Watermark", code: 3, userInfo: [NSLocalizedDescriptionKey: "Cannot encode \(input.path)"])
    }
    try encoded.write(to: output, options: .atomic)
    return (box, output)
}

let args = Array(CommandLine.arguments.dropFirst())
if args.first == "--batch", args.count == 5 {
    let manifestURL = URL(fileURLWithPath: args[1])
    let sourceRoot = URL(fileURLWithPath: args[2], isDirectory: true)
    let outputRoot = URL(fileURLWithPath: args[3], isDirectory: true)
    let pageOutputRoot = args[3].hasPrefix("./") ? String(args[3].dropFirst(2)) : args[3]
    let resultsURL = URL(fileURLWithPath: args[4])
    let manifestData = try Data(contentsOf: manifestURL)
    let lines = String(decoding: manifestData, as: UTF8.self).split(whereSeparator: \.isNewline)
    let imageDirectories = try FileManager.default.contentsOfDirectory(
        at: sourceRoot,
        includingPropertiesForKeys: [.isDirectoryKey],
        options: [.skipsHiddenFiles]
    )
    var directoriesByProduct: [String: URL] = [:]
    for directory in imageDirectories {
        let name = directory.lastPathComponent
        guard let separator = name.firstIndex(of: "_") else { continue }
        let productID = String(name[..<separator])
        if productID.allSatisfy(\.isNumber) {
            directoriesByProduct[productID] = directory
        }
    }
    try FileManager.default.createDirectory(at: resultsURL.deletingLastPathComponent(), withIntermediateDirectories: true)
    var completedByKey: [String: [String: Any]] = [:]
    if FileManager.default.fileExists(atPath: resultsURL.path) {
        let existing = try Data(contentsOf: resultsURL)
        let workspace = URL(fileURLWithPath: FileManager.default.currentDirectoryPath, isDirectory: true)
        for line in String(decoding: existing, as: UTF8.self).split(whereSeparator: \.isNewline) {
            guard let item = try? JSONSerialization.jsonObject(with: Data(line.utf8)) as? [String: Any],
                  item["status"] as? String == "complete",
                  let key = item["object_key"] as? String,
                  let localSource = item["local_src"] as? String else { continue }
            let relative = localSource.hasPrefix("../") ? String(localSource.dropFirst(3)) : localSource
            let output = workspace.appendingPathComponent(relative)
            if FileManager.default.fileExists(atPath: output.path) {
                completedByKey[key] = item
            }
        }
    } else if !FileManager.default.createFile(atPath: resultsURL.path, contents: nil) {
        throw NSError(domain: "Watermark", code: 4, userInfo: [NSLocalizedDescriptionKey: "Cannot create \(resultsURL.path)"])
    }
    let resultsHandle = try FileHandle(forWritingTo: resultsURL)
    try resultsHandle.seekToEnd()
    let stateLock = NSLock()
    var cleanedCount = completedByKey.values.filter { $0["watermark_removed"] as? Bool == true }.count
    var copiedCount = completedByKey.count - cleanedCount
    var failedCount = 0
    let reusedCount = completedByKey.count
    var finishedCount = 0

    var productIDs = Set<String>()
    for line in lines {
        if let item = try? JSONSerialization.jsonObject(with: Data(line.utf8)) as? [String: Any],
           let productID = item["product_id"] as? String {
            productIDs.insert(productID)
        }
    }
    for productID in productIDs {
        try FileManager.default.createDirectory(at: outputRoot.appendingPathComponent(productID, isDirectory: true), withIntermediateDirectories: true)
    }

    DispatchQueue.concurrentPerform(iterations: lines.count) { index in
        let line = lines[index]
        var objectKeyForError: String?
        do {
            guard let item = try JSONSerialization.jsonObject(with: Data(line.utf8)) as? [String: Any],
                  let productID = item["product_id"] as? String,
                  let archiveMember = item["archive_member"] as? String,
                  let objectKey = item["object_key"] as? String else {
                throw NSError(domain: "Watermark", code: 5, userInfo: [NSLocalizedDescriptionKey: "Invalid manifest line \(index + 1)"])
            }
            objectKeyForError = objectKey
            if completedByKey[objectKey] != nil {
                stateLock.lock()
                finishedCount += 1
                if finishedCount % 250 == 0 || finishedCount == lines.count {
                    print("processed \(finishedCount)/\(lines.count), reused \(reusedCount), cleaned \(cleanedCount), unchanged \(copiedCount), failed \(failedCount)")
                    fflush(stdout)
                }
                stateLock.unlock()
                return
            }
            guard let productDirectory = directoriesByProduct[productID] else {
                throw NSError(domain: "Watermark", code: 6, userInfo: [NSLocalizedDescriptionKey: "No source directory for product \(productID)"])
            }
            let sourceName = URL(fileURLWithPath: archiveMember).lastPathComponent
            let input = productDirectory.appendingPathComponent(sourceName)
            let basename = URL(fileURLWithPath: objectKey).deletingPathExtension().lastPathComponent
            let outputBase = outputRoot.appendingPathComponent(productID, isDirectory: true).appendingPathComponent(basename)
            let result: ([String: Any], Bool) = try autoreleasepool {
                for ext in ["jpg", "jpeg", "png", "gif", "webp"] {
                    let candidate = outputBase.appendingPathExtension(ext)
                    if FileManager.default.fileExists(atPath: candidate.path) {
                        try FileManager.default.removeItem(at: candidate)
                    }
                }
                let (detection, output) = try process(input, outputBase)
                let localSource = "../\(pageOutputRoot)/\(productID)/\(output.lastPathComponent)"
                let row: [String: Any] = [
                    "object_key": objectKey,
                    "product_id": productID,
                    "local_src": localSource,
                    "watermark_removed": detection != nil,
                    "red_pixels": detection?.pixels ?? 0,
                    "status": "complete"
                ]
                return (row, detection != nil)
            }
            let encoded = try JSONSerialization.data(withJSONObject: result.0, options: [.sortedKeys])
            stateLock.lock()
            do {
                try resultsHandle.write(contentsOf: encoded + Data([10]))
            } catch {
                stateLock.unlock()
                throw error
            }
            if result.1 { cleanedCount += 1 } else { copiedCount += 1 }
            finishedCount += 1
            if finishedCount % 250 == 0 || finishedCount == lines.count {
                print("processed \(finishedCount)/\(lines.count), reused \(reusedCount), cleaned \(cleanedCount), unchanged \(copiedCount), failed \(failedCount)")
                fflush(stdout)
            }
            stateLock.unlock()
        } catch {
            let failure: [String: Any] = ["line": index + 1, "object_key": objectKeyForError ?? "", "status": "error", "error": error.localizedDescription]
            let encoded = (try? JSONSerialization.data(withJSONObject: failure, options: [.sortedKeys])) ?? Data()
            stateLock.lock()
            failedCount += 1
            finishedCount += 1
            try? resultsHandle.write(contentsOf: encoded + Data([10]))
            if finishedCount % 250 == 0 || finishedCount == lines.count {
                print("processed \(finishedCount)/\(lines.count), reused \(reusedCount), cleaned \(cleanedCount), unchanged \(copiedCount), failed \(failedCount)")
                fflush(stdout)
            }
            stateLock.unlock()
        }
    }
    try resultsHandle.close()
    if failedCount > 0 {
        fputs("Completed with \(failedCount) errors; catalog data was not changed.\n", stderr)
        exit(1)
    }
} else if args.count == 2 {
    let input = URL(fileURLWithPath: args[0])
    let output = URL(fileURLWithPath: args[1])
    let outputBase = output.deletingPathExtension()
    let (box, result) = try process(input, outputBase)
    if let box {
        print("cleaned \(box.left),\(box.top)-\(box.right),\(box.bottom) red=\(box.pixels) -> \(result.path)")
    } else {
        print("no watermark -> \(result.path)")
    }
} else {
    fputs("Usage: clean_catalog_healong_watermark.swift INPUT OUTPUT\n       clean_catalog_healong_watermark.swift --batch MANIFEST SOURCE_ROOT OUTPUT_ROOT RESULTS\n", stderr)
    exit(2)
}
