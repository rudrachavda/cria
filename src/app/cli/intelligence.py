"""
Intelligence and reasoning capabilities for the cria AI agent.
Provides smart decision-making and context-aware tool selection.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

class AgentIntelligence:
    """Intelligent reasoning and decision-making for the agent."""
    
    def __init__(self):
        self.context_history = []
        self.learned_patterns = {}
        self.project_insights = {}
    
    def analyze_user_intent(self, user_goal: str) -> Dict[str, Any]:
        """
        Analyze user intent and suggest optimal approach.
        
        Args:
            user_goal: The user's stated goal
            
        Returns:
            Dict containing analysis and recommendations
        """
        intent_analysis = {
            "intent_type": "unknown",
            "complexity": "medium",
            "suggested_tools": [],
            "approach": "exploratory",
            "confidence": 0.5
        }
        
        goal_lower = user_goal.lower()
        
        # Intent classification
        if any(word in goal_lower for word in ["find", "search", "locate", "where", "which"]):
            intent_analysis["intent_type"] = "search"
            intent_analysis["suggested_tools"] = ["get_project_overview", "explore_codebase", "find_code_patterns", "navigate_to_symbol"]
            intent_analysis["confidence"] = 0.8
        elif any(word in goal_lower for word in ["analyze", "understand", "explain", "what", "how"]):
            intent_analysis["intent_type"] = "analysis"
            intent_analysis["suggested_tools"] = ["get_project_overview", "analyze_file", "get_code_flow", "get_file_dependencies"]
            intent_analysis["confidence"] = 0.8
        elif any(word in goal_lower for word in ["create", "write", "add", "implement", "build"]):
            intent_analysis["intent_type"] = "creation"
            intent_analysis["suggested_tools"] = ["get_project_overview", "analyze_file", "write_file", "execute_with_context"]
            intent_analysis["confidence"] = 0.7
        elif any(word in goal_lower for word in ["fix", "debug", "error", "problem", "issue"]):
            intent_analysis["intent_type"] = "debugging"
            intent_analysis["suggested_tools"] = ["get_project_overview", "find_code_patterns", "analyze_file", "execute_with_context"]
            intent_analysis["confidence"] = 0.8
        elif any(word in goal_lower for word in ["improve", "optimize", "refactor", "better"]):
            intent_analysis["intent_type"] = "improvement"
            intent_analysis["suggested_tools"] = ["get_project_overview", "analyze_file", "suggest_improvements", "get_project_health"]
            intent_analysis["confidence"] = 0.7
        
        # Complexity assessment
        if any(word in goal_lower for word in ["all", "entire", "everything", "complete", "comprehensive"]):
            intent_analysis["complexity"] = "high"
        elif any(word in goal_lower for word in ["simple", "quick", "just", "only"]):
            intent_analysis["complexity"] = "low"
        
        # Approach recommendation
        if intent_analysis["intent_type"] == "search":
            intent_analysis["approach"] = "pattern_matching"
        elif intent_analysis["intent_type"] == "analysis":
            intent_analysis["approach"] = "deep_dive"
        elif intent_analysis["intent_type"] == "creation":
            intent_analysis["approach"] = "iterative_build"
        elif intent_analysis["intent_type"] == "debugging":
            intent_analysis["approach"] = "systematic_investigation"
        elif intent_analysis["intent_type"] == "improvement":
            intent_analysis["approach"] = "assessment_first"
        
        return intent_analysis
    
    def suggest_next_tool(self, current_context: str, available_tools: List[str], 
                         previous_actions: List[Dict]) -> str:
        """
        Suggest the next best tool based on current context and history.
        
        Args:
            current_context: Current state/observation
            available_tools: List of available tool names
            previous_actions: History of previous actions
            
        Returns:
            Suggested tool name
        """
        context_lower = current_context.lower()
        
        # If we have no context, start with project overview
        if not previous_actions or "project_overview" not in str(previous_actions):
            return "get_project_overview"
        
        # If we found files but haven't analyzed them
        if "files found" in context_lower and not any("analyze_file" in str(action) for action in previous_actions[-3:]):
            return "analyze_file"
        
        # If we're looking for specific patterns
        if any(word in context_lower for word in ["pattern", "search", "find"]):
            return "find_code_patterns"
        
        # If we need to understand code structure
        if any(word in context_lower for word in ["function", "class", "method"]):
            return "navigate_to_symbol"
        
        # If we need to understand relationships
        if any(word in context_lower for word in ["import", "dependency", "reference"]):
            return "get_file_dependencies"
        
        # If we're analyzing code flow
        if any(word in context_lower for word in ["flow", "entry", "main", "start"]):
            return "get_code_flow"
        
        # Default to exploration
        return "explore_codebase"
    
    def extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text for better context understanding."""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", 
            "has", "had", "do", "does", "did", "will", "would", "could", "should",
            "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"
        }
        
        # Extract words that look like code terms
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return list(set(key_terms))
    
    def generate_smart_plan(self, user_goal: str, project_context: str = None) -> List[Dict[str, Any]]:
        """
        Generate a smart execution plan based on user goal and project context.
        
        Args:
            user_goal: The user's goal
            project_context: Optional project context information
            
        Returns:
            List of planned actions
        """
        intent = self.analyze_user_intent(user_goal)
        key_terms = self.extract_key_terms(user_goal)
        
        plan = []
        
        # For file reading tasks, start with exploration instead of full overview
        if "read" in user_goal.lower() and "file" in user_goal.lower():
            plan.append({
                "tool": "explore_codebase",
                "args": {"pattern": "**/*.py", "max_files": 50},
                "reason": "Find all Python files to read and analyze",
                "priority": "high"
            })
            plan.append({
                "tool": "read_multiple_files",
                "reason": "Read all relevant files to understand the project",
                "priority": "high"
            })
            if "write" in user_goal.lower() and "readme" in user_goal.lower():
                plan.append({
                    "tool": "write_file",
                    "reason": "Write comprehensive description to README.md",
                    "priority": "high"
                })
        else:
            # Always start with project overview for other tasks
            plan.append({
                "tool": "get_project_overview",
                "reason": "Understand project structure and context",
                "priority": "high"
            })
        
        # Add exploration based on intent
        if intent["intent_type"] == "search":
            if key_terms:
                plan.append({
                    "tool": "find_code_patterns",
                    "args": {"pattern": "|".join(key_terms)},
                    "reason": f"Search for patterns related to: {', '.join(key_terms)}",
                    "priority": "high"
                })
            plan.append({
                "tool": "explore_codebase",
                "reason": "Explore codebase structure to find relevant files",
                "priority": "medium"
            })
        
        elif intent["intent_type"] == "analysis":
            plan.append({
                "tool": "explore_codebase",
                "args": {"file_type": "py", "max_files": 10},
                "reason": "Find Python files to analyze",
                "priority": "high"
            })
            plan.append({
                "tool": "analyze_file",
                "reason": "Analyze key files for structure and functionality",
                "priority": "high"
            })
        
        elif intent["intent_type"] == "creation":
            plan.append({
                "tool": "get_project_health",
                "reason": "Assess project health before making changes",
                "priority": "medium"
            })
            plan.append({
                "tool": "explore_codebase",
                "args": {"file_type": "py"},
                "reason": "Understand existing code structure",
                "priority": "high"
            })
        
        elif intent["intent_type"] == "debugging":
            plan.append({
                "tool": "find_code_patterns",
                "args": {"pattern": "error|exception|traceback|debug"},
                "reason": "Look for error-related code patterns",
                "priority": "high"
            })
            plan.append({
                "tool": "get_project_health",
                "reason": "Check overall project health for issues",
                "priority": "medium"
            })
        
        elif intent["intent_type"] == "improvement":
            plan.append({
                "tool": "get_project_health",
                "reason": "Get comprehensive health assessment",
                "priority": "high"
            })
            plan.append({
                "tool": "suggest_improvements",
                "reason": "Get specific improvement suggestions",
                "priority": "high"
            })
        
        return plan
    
    def should_continue(self, current_observation: str, iteration: int, max_iterations: int) -> Tuple[bool, str]:
        """
        Determine if the agent should continue or stop.
        
        Args:
            current_observation: Current observation/result
            iteration: Current iteration number
            max_iterations: Maximum allowed iterations
            
        Returns:
            Tuple of (should_continue, reason)
        """
        if iteration >= max_iterations:
            return False, "Maximum iterations reached"
        
        obs_lower = current_observation.lower()
        
        # Only stop if we've actually completed the task (written to README.md)
        if "successfully wrote" in obs_lower and "readme.md" in obs_lower:
            return False, "Task completed - README.md has been written"
        
        # Don't stop just because we found files - we need to read them and write README
        if "found" in obs_lower and "files" in obs_lower and "matching" in obs_lower:
            return True, "Found files, need to read and process them"
        
        # Don't stop just because we read files - we need to write the summary
        if "project analysis summary" in obs_lower or "file analysis" in obs_lower:
            return True, "Read files, need to write summary to README.md"
        
        # Stop if we're stuck in an error loop
        if "error" in obs_lower and iteration > 3:
            return False, "Too many errors encountered"
        
        # Don't stop if we haven't found files yet
        if "no files found" in obs_lower and iteration < 5:
            return True, "Still searching for files"
        
        # Continue if we're still exploring or analyzing
        if any(phrase in obs_lower for phrase in ["analyzing", "exploring", "searching", "processing"]):
            return True, "Still processing"
        
        # Continue if we have more work to do
        if any(phrase in obs_lower for phrase in ["next", "continue", "more", "additional"]):
            return True, "More work indicated"
        
        # Default to continue for exploration
        return True, "Continuing exploration"
    
    def learn_from_interaction(self, user_goal: str, actions_taken: List[Dict], 
                             final_result: str, success: bool):
        """
        Learn from the interaction to improve future performance.
        
        Args:
            user_goal: Original user goal
            actions_taken: List of actions taken
            final_result: Final result
            success: Whether the interaction was successful
        """
        # Store successful patterns
        if success:
            key_terms = self.extract_key_terms(user_goal)
            for term in key_terms:
                if term not in self.learned_patterns:
                    self.learned_patterns[term] = []
                self.learned_patterns[term].extend([action["tool"] for action in actions_taken])
        
        # Store project insights
        if "project" in final_result.lower():
            self.project_insights[user_goal] = {
                "success": success,
                "actions": len(actions_taken),
                "result_length": len(final_result)
            }
    
    def get_contextual_suggestions(self, current_state: str) -> List[str]:
        """
        Get contextual suggestions based on current state.
        
        Args:
            current_state: Current state description
            
        Returns:
            List of suggestions
        """
        suggestions = []
        state_lower = current_state.lower()
        
        if "file not found" in state_lower:
            suggestions.extend([
                "Try using explore_codebase to find similar files",
                "Check the project structure with get_project_overview",
                "Use find_code_patterns to search for related content"
            ])
        
        elif "error" in state_lower:
            suggestions.extend([
                "Analyze the error context with analyze_file",
                "Search for similar error patterns with find_code_patterns",
                "Check project health with get_project_health"
            ])
        
        elif "import" in state_lower:
            suggestions.extend([
                "Use get_file_dependencies to understand import relationships",
                "Navigate to the imported symbol with navigate_to_symbol",
                "Check if the module exists in the project"
            ])
        
        elif "function" in state_lower or "class" in state_lower:
            suggestions.extend([
                "Use navigate_to_symbol to find the specific function/class",
                "Analyze the file containing the symbol",
                "Check dependencies and usage patterns"
            ])
        
        return suggestions
