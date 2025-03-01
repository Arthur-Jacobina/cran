/**
 * Extracts a clean message from AI response content
 * @param {string} content - Raw AI response content
 * @return {string} Cleaned message text
 */
export function extractCleanMessage(content) {
    if (!content) return '';
    
    // If content is already a simple string without nesting indicators, return it
    if (typeof content === 'string' && 
        !content.includes('{') && 
        !content.includes('AIMessage') && 
        !content.startsWith("{'messages'")) {
      return content;
    }
    
    try {
      // Pattern to extract content from AIMessage
      const aiMessagePattern = /AIMessage\(content="([^"]+?)"/;
      const simpleContentPattern = /content="([^"]+?)"/;
      const finalAIMessagePattern = /AIMessage\(content="([^"]+?)".*?id='[^']+?-\d+'/s;
      
      // Try to extract the most recent/final AIMessage content
      const finalMatch = content.match(finalAIMessagePattern);
      if (finalMatch && finalMatch[1]) {
        return cleanupContent(finalMatch[1]);
      }
      
      // Try to find any AIMessage content
      const aiMatch = content.match(aiMessagePattern);
      if (aiMatch && aiMatch[1]) {
        return cleanupContent(aiMatch[1]);
      }
      
      // Try to find any content field
      const contentMatch = content.match(simpleContentPattern);
      if (contentMatch && contentMatch[1]) {
        return cleanupContent(contentMatch[1]);
      }
      
      // If we have a response with emojis (common pattern in the provided data)
      if (content.includes('💕') || 
          content.includes('🥰') || 
          content.includes('😊')) {
        // Split by the first emoji
        const parts = content.split(/[💕🥰😊]/);
        if (parts.length > 0 && parts[0].includes('}')) {
          // Extract just the text after the JSON part
          const afterJson = parts[0].split('}').pop();
          if (afterJson && afterJson.trim()) {
            return afterJson.trim();
          }
        }
      }
      
      // Handle nested JSON-like structure when quotes are escaped
      if (content.includes("\\'messages\\'")) {
        // Find the last AIMessage in the chain
        const matches = [...content.matchAll(/AIMessage\(content=\\"([^\\]+?)\\"/g)];
        if (matches.length > 0) {
          // Get the last match (most recent message)
          const lastMatch = matches[matches.length - 1];
          if (lastMatch && lastMatch[1]) {
            return cleanupContent(lastMatch[1]);
          }
        }
      }
      
      // Last resort - extract any text after the last closing brace
      const afterJson = content.split(/}[^{]*$/);
      if (afterJson.length > 1 && afterJson[afterJson.length-1].trim()) {
        return afterJson[afterJson.length-1].trim();
      }
      
    } catch (err) {
      console.error('Error extracting clean message:', err);
    }
    
    // If all else fails, return the original content
    return content;
  }
  
  /**
   * Clean up extracted content
   * @param {string} content - Content to clean
   * @return {string} Cleaned content
   */
  function cleanupContent(content) {
    return content
      .replace(/\\'/g, "'")
      .replace(/\\"/g, '"')
      .replace(/\\n/g, '\n')
      .replace(/\\t/g, '\t')
      .trim();
  }
  
  /**
   * Extracts reasoning steps from AI response if present
   * @param {string} content - Raw AI response content 
   * @return {string[]} Array of reasoning steps
   */
  export function extractReasoningSteps(content) {
    if (!content) return [];
    
    try {
      // Look for reasoning section between markers or in specific format
      const reasoningPattern = /reasoning_steps: \[(.*?)\]/s;
      const match = content.match(reasoningPattern);
      
      if (match && match[1]) {
        // Split by commas but preserve commas in quotes
        return match[1]
          .split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/)
          .map(step => step.trim().replace(/^["']|["']$/g, ''));
      }
    } catch (err) {
      console.error('Error extracting reasoning steps:', err);
    }
    
    return [];
  }
  
  /**
   * Format system logs based on metadata and context
   * @param {object} metadata - Message metadata
   * @param {object} context - Chat context
   * @return {object} Formatted memory log and execution flow
   */
  export function formatSystemLogs(metadata: any, context: any) {
    let memoryLog = '';
    let executionFlow = '';
    
    try {
      // Format memory log from context
      if (context) {
        memoryLog = [
          context.memory_count ? `Memory count: ${context.memory_count}` : '',
          context.user_interests?.length ? `User interests: ${context.user_interests.join(', ')}` : '',
          context.user_mood ? `User mood: ${context.user_mood}` : '',
          context.relevant_memories?.length ? `Relevant memories: ${context.relevant_memories.join(', ')}` : ''
        ].filter(Boolean).join('\n');
      }
      
      // Format execution flow from metadata
      if (metadata) {
        const tokens = metadata.token_usage;
        const steps = [];
        
        if (tokens) {
          steps.push(`→ Processed input (${tokens.prompt_tokens} tokens)`);
          
          if (tokens.completion_tokens_details?.reasoning_tokens > 0) {
            steps.push(`→ Applied reasoning (${tokens.completion_tokens_details.reasoning_tokens} tokens)`);
          }
          
          steps.push(`→ Generated response (${tokens.completion_tokens} tokens)`);
          steps.push(`→ Total processing: ${tokens.total_tokens} tokens`);
        } else {
          steps.push('→ Processing input → Generating response');
        }
        
        executionFlow = steps.join('\n');
      }
    } catch (err) {
      console.error('Error formatting system logs:', err);
      memoryLog = 'Error parsing memory data';
      executionFlow = 'Error parsing execution flow';
    }
    
    return { memoryLog, executionFlow };
  }