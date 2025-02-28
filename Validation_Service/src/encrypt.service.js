require("dotenv").config();
const axios = require("axios");
const TenSeal = require("tenseal");

async function encryptVector(vector) {
  var res = null;
  try {
    const context = await TenSeal.Context({
      scheme: "ckks",
      polyModulusDegree: 8192,
      coeffModulus: [60, 40, 40, 60],
      scale: Math.pow(2, 40),
    });

    const plaintextVector = context.vector(vector);
    const encryptedVector = plaintextVector.encrypt();
    const serialized = encryptedVector.serialize();

    encryptedVector.delete();
    plaintextVector.delete();
    context.delete();

    res.status(200).json({
      encrypted: serialized.toString("base64"),
    });
  } catch (error) {
    console.error("Encryption error:", error);

    if (error.message.includes("context")) {
      return res.status(500).json({
        error: "Encryption context initialization failed",
      });
    }

    res.status(500).json({
      error: "Internal server error during encryption",
      message: error.message,
    });

    return res;
  }

  module.exports = {
    encryptVector,
  };
}
