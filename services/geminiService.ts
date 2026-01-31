import { GoogleGenAI } from "@google/genai";

// Initialize the Gemini API client
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export const generateOtpMessage = async (
  serviceName: string,
  countryName: string
): Promise<string> => {
  try {
    const model = 'gemini-3-flash-preview';
    const prompt = `
      Generate a realistic SMS verification message for "${serviceName}".
      The recipient is in "${countryName}".
      Include a realistic 4-8 digit verification code.
      The message should be in the language appropriate for ${countryName} (or English if commonly used there).
      Only return the message text, nothing else.
      Do not include quotes.
    `;

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
    });

    return response.text?.trim() || `Code: ${Math.floor(100000 + Math.random() * 900000)}`;
  } catch (error) {
    console.error("Gemini API Error:", error);
    return `Your ${serviceName} code is ${Math.floor(100000 + Math.random() * 900000)}.`;
  }
};