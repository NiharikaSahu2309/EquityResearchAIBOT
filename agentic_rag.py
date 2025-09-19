"""
Agentic RAG System for Equity Research Assistant
This module implements an intelligent agent that can reason, plan, and use multiple tools
to provide more precise and comprehensive answers.
"""

import json
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

class FinancialAnalysisAgent:
    """
    Intelligent agent for financial analysis that can:
    1. Plan multi-step analysis
    2. Use multiple data sources
    3. Perform calculations and validations
    4. Provide structured insights
    """
    
    def __init__(self, rag_pipeline, groq_client, max_processing_time=90):
        self.rag_pipeline = rag_pipeline
        self.groq_client = groq_client
        self.max_processing_time = max_processing_time  # Maximum processing time in seconds
        self.analysis_tools = {
            'search': self._search_documents,
            'calculate': self._perform_calculations,
            'analyze_trends': self._analyze_trends,
            'risk_assessment': self._assess_risk,
            'compare': self._compare_entities,
            'summarize': self._summarize_findings
        }
        
    def process_query(self, user_query: str, context_data: Dict = None) -> Dict[str, Any]:
        """
        Main entry point for agentic RAG processing with timeout handling
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze the query and create a plan
            plan = self._create_analysis_plan(user_query, context_data)
            
            # Check timeout
            if time.time() - start_time > self.max_processing_time:
                return self._timeout_response("Planning phase exceeded time limit")
            
            # Step 2: Execute the plan step by step
            results = self._execute_plan(plan, user_query, context_data, start_time)
            
            # Check timeout
            if time.time() - start_time > self.max_processing_time:
                return self._timeout_response("Execution phase exceeded time limit")
            
            # Step 3: Synthesize final answer
            final_answer = self._synthesize_answer(user_query, plan, results)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'answer': final_answer,
                'plan': plan,
                'intermediate_results': results,
                'confidence': self._calculate_confidence(results),
                'sources': self._extract_sources(results),
                'processing_time': round(processing_time, 2)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'answer': f"I encountered an error while processing your query: {str(e)}",
                'processing_time': round(time.time() - start_time, 2)
            }
    
    def _timeout_response(self, reason: str) -> Dict[str, Any]:
        """Generate a timeout response"""
        return {
            'success': False,
            'error': f"Processing timeout: {reason}",
            'answer': "I apologize, but your query is taking longer than expected to process. Please try a simpler question or break down your request into smaller parts.",
            'timeout': True
        }
    
    def _create_analysis_plan(self, query: str, context_data: Dict = None) -> List[Dict]:
        """
        Create a step-by-step analysis plan based on the query
        """
        # Use LLM to understand the query and create a plan
        planning_prompt = f"""
        Analyze this financial query and create a step-by-step analysis plan.
        
        Query: {query}
        
        Available tools:
        - search: Search through uploaded documents
        - calculate: Perform financial calculations
        - analyze_trends: Analyze trends in data
        - risk_assessment: Assess financial risks
        - compare: Compare different entities/periods
        - summarize: Summarize findings
        
        Available context data: {list(context_data.keys()) if context_data else 'None'}
        
        Create a JSON plan with steps like:
        [
            {{"step": 1, "tool": "search", "description": "Search for relevant financial data", "query": "specific search terms"}},
            {{"step": 2, "tool": "calculate", "description": "Calculate key metrics", "inputs": ["data_needed"]}},
            ...
        ]
        
        Focus on providing precise, data-driven analysis. Return only the JSON array.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": planning_prompt}],
                temperature=0.1,
                max_tokens=500,  # Reduced for faster response
                timeout=10  # 10 second timeout for planning
            )
            
            plan_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', plan_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return plan
            else:
                # Fallback plan
                return self._create_fallback_plan(query)
                
        except Exception as e:
            print(f"Error creating plan: {e}")
            return self._create_fallback_plan(query)
    
    def _create_fallback_plan(self, query: str) -> List[Dict]:
        """
        Create a basic fallback plan when LLM planning fails
        """
        plan = [
            {"step": 1, "tool": "search", "description": "Search for relevant information", "query": query},
            {"step": 2, "tool": "summarize", "description": "Summarize findings", "inputs": ["search_results"]}
        ]
        
        # Add specific steps based on query content
        if any(keyword in query.lower() for keyword in ['calculate', 'ratio', 'metric', 'performance']):
            plan.insert(1, {"step": 2, "tool": "calculate", "description": "Perform calculations", "inputs": ["search_results"]})
        
        if any(keyword in query.lower() for keyword in ['trend', 'growth', 'change', 'over time']):
            plan.insert(-1, {"step": len(plan), "tool": "analyze_trends", "description": "Analyze trends", "inputs": ["search_results"]})
        
        if any(keyword in query.lower() for keyword in ['risk', 'volatility', 'uncertainty']):
            plan.insert(-1, {"step": len(plan), "tool": "risk_assessment", "description": "Assess risks", "inputs": ["search_results"]})
        
        # Renumber steps
        for i, step in enumerate(plan):
            step["step"] = i + 1
            
        return plan
    
    def _execute_plan(self, plan: List[Dict], original_query: str, context_data: Dict = None, start_time: float = None) -> Dict[str, Any]:
        """
        Execute the analysis plan step by step with timeout handling
        """
        results = {'steps': {}}
        accumulated_data = {}
        
        for step in plan:
            # Check timeout before each step
            if start_time and time.time() - start_time > self.max_processing_time:
                results['steps'][f'timeout_at_step_{step["step"]}'] = {
                    'tool': 'timeout',
                    'description': 'Processing stopped due to timeout',
                    'result': 'Timeout reached during execution',
                    'success': False
                }
                break
                
            step_num = step['step']
            tool = step['tool']
            
            try:
                if tool in self.analysis_tools:
                    # Prepare inputs for the tool
                    if tool == 'search':
                        search_query = step.get('query', original_query)
                        result = self.analysis_tools[tool](search_query)
                    else:
                        # Use accumulated data and context
                        inputs = {
                            'query': original_query,
                            'step_config': step,
                            'accumulated_data': accumulated_data,
                            'context_data': context_data or {}
                        }
                        result = self.analysis_tools[tool](inputs)
                    
                    results['steps'][step_num] = {
                        'tool': tool,
                        'description': step['description'],
                        'result': result,
                        'success': True
                    }
                    
                    # Accumulate data for next steps
                    accumulated_data[f'step_{step_num}'] = result
                    
                else:
                    results['steps'][step_num] = {
                        'tool': tool,
                        'description': step['description'],
                        'result': f"Tool '{tool}' not available",
                        'success': False
                    }
                    
            except Exception as e:
                results['steps'][step_num] = {
                    'tool': tool,
                    'description': step['description'],
                    'result': f"Error: {str(e)}",
                    'success': False
                }
        
        return results
    
    def _search_documents(self, query: str) -> Dict[str, Any]:
        """
        Enhanced document search with intelligent result processing
        """
        try:
            # Get search results
            raw_results = self.rag_pipeline.search_documents(query, n_results=10)
            
            if not raw_results or 'error' in raw_results[0]:
                return {'documents': [], 'summary': 'No relevant documents found'}
            
            # Process and enhance results
            processed_results = []
            for result in raw_results:
                processed_result = {
                    'content': result['content'],
                    'source': result['metadata'].get('filename', 'Unknown'),
                    'relevance': result['relevance_score'],
                    'type': self._detect_content_type(result['content']),
                    'key_metrics': self._extract_key_metrics(result['content'])
                }
                processed_results.append(processed_result)
            
            # Create summary
            summary = self._create_search_summary(processed_results, query)
            
            return {
                'documents': processed_results,
                'summary': summary,
                'total_found': len(processed_results)
            }
            
        except Exception as e:
            return {'error': str(e), 'documents': []}
    
    def _perform_calculations(self, inputs: Dict) -> Dict[str, Any]:
        """
        Perform financial calculations on the data
        """
        try:
            accumulated_data = inputs.get('accumulated_data', {})
            query = inputs.get('query', '')
            
            calculations = {}
            
            # Extract numerical data from search results
            numerical_data = self._extract_numerical_data(accumulated_data)
            
            if numerical_data:
                # Common financial calculations
                if any(term in query.lower() for term in ['ratio', 'pe', 'pb', 'roe', 'roa']):
                    calculations.update(self._calculate_financial_ratios(numerical_data))
                
                if any(term in query.lower() for term in ['growth', 'change', 'increase', 'decrease']):
                    calculations.update(self._calculate_growth_metrics(numerical_data))
                
                if any(term in query.lower() for term in ['average', 'mean', 'median']):
                    calculations.update(self._calculate_statistical_metrics(numerical_data))
                
                if any(term in query.lower() for term in ['return', 'performance', 'yield']):
                    calculations.update(self._calculate_return_metrics(numerical_data))
            
            return {
                'calculations': calculations,
                'data_used': list(numerical_data.keys()) if numerical_data else [],
                'insights': self._generate_calculation_insights(calculations)
            }
            
        except Exception as e:
            return {'error': str(e), 'calculations': {}}
    
    def _analyze_trends(self, inputs: Dict) -> Dict[str, Any]:
        """
        Analyze trends in the data
        """
        try:
            accumulated_data = inputs.get('accumulated_data', {})
            
            trends = {}
            
            # Extract time series data
            time_series_data = self._extract_time_series_data(accumulated_data)
            
            for metric, data in time_series_data.items():
                if len(data) >= 2:
                    trend_analysis = {
                        'direction': self._determine_trend_direction(data),
                        'volatility': self._calculate_volatility(data),
                        'recent_change': self._calculate_recent_change(data),
                        'pattern': self._identify_pattern(data)
                    }
                    trends[metric] = trend_analysis
            
            return {
                'trends': trends,
                'summary': self._create_trend_summary(trends)
            }
            
        except Exception as e:
            return {'error': str(e), 'trends': {}}
    
    def _assess_risk(self, inputs: Dict) -> Dict[str, Any]:
        """
        Assess financial risks
        """
        try:
            accumulated_data = inputs.get('accumulated_data', {})
            
            risk_assessment = {
                'market_risk': 'Medium',  # Placeholder
                'credit_risk': 'Low',     # Placeholder
                'liquidity_risk': 'Low',  # Placeholder
                'operational_risk': 'Medium'  # Placeholder
            }
            
            # Extract relevant data for risk assessment
            numerical_data = self._extract_numerical_data(accumulated_data)
            
            if numerical_data:
                # Calculate risk metrics
                volatility_metrics = self._calculate_risk_metrics(numerical_data)
                risk_assessment.update(volatility_metrics)
            
            return {
                'risk_assessment': risk_assessment,
                'recommendations': self._generate_risk_recommendations(risk_assessment)
            }
            
        except Exception as e:
            return {'error': str(e), 'risk_assessment': {}}
    
    def _compare_entities(self, inputs: Dict) -> Dict[str, Any]:
        """
        Compare different entities or time periods
        """
        try:
            accumulated_data = inputs.get('accumulated_data', {})
            
            # Extract comparable data
            comparison_data = self._extract_comparison_data(accumulated_data)
            
            comparisons = {}
            if comparison_data:
                for metric, values in comparison_data.items():
                    if len(values) >= 2:
                        comparisons[metric] = {
                            'values': values,
                            'best_performer': max(values, key=lambda x: x['value'])['entity'],
                            'worst_performer': min(values, key=lambda x: x['value'])['entity'],
                            'average': np.mean([v['value'] for v in values]),
                            'spread': max([v['value'] for v in values]) - min([v['value'] for v in values])
                        }
            
            return {
                'comparisons': comparisons,
                'summary': self._create_comparison_summary(comparisons)
            }
            
        except Exception as e:
            return {'error': str(e), 'comparisons': {}}
    
    def _summarize_findings(self, inputs: Dict) -> Dict[str, Any]:
        """
        Summarize all findings into a coherent response
        """
        try:
            accumulated_data = inputs.get('accumulated_data', {})
            query = inputs.get('query', '')
            
            # Extract key findings from all steps
            key_findings = []
            sources = []
            
            for step_key, step_data in accumulated_data.items():
                if isinstance(step_data, dict):
                    if 'summary' in step_data:
                        key_findings.append(step_data['summary'])
                    if 'documents' in step_data:
                        sources.extend([doc['source'] for doc in step_data['documents']])
                    if 'calculations' in step_data and step_data['calculations']:
                        key_findings.append(f"Key calculations: {list(step_data['calculations'].keys())}")
            
            # Generate comprehensive summary using LLM
            summary_prompt = f"""
            Based on the financial analysis conducted, provide a comprehensive summary for this query:
            
            Query: {query}
            
            Key Findings:
            {chr(10).join(f"- {finding}" for finding in key_findings)}
            
            Sources: {', '.join(set(sources))}
            
            Provide a clear, structured summary that directly answers the user's question with specific data points and insights.
            """
            
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": summary_prompt}],
                    temperature=0.2,
                    max_tokens=1500
                )
                
                summary = response.choices[0].message.content.strip()
                
            except Exception as e:
                summary = f"Summary of findings: {'. '.join(key_findings)}"
            
            return {
                'summary': summary,
                'key_findings': key_findings,
                'sources_used': list(set(sources))
            }
            
        except Exception as e:
            return {'error': str(e), 'summary': 'Could not generate summary'}
    
    def _synthesize_answer(self, query: str, plan: List[Dict], results: Dict) -> str:
        """
        Synthesize the final answer from all analysis steps
        """
        try:
            # Extract the final summary if available
            final_summary = None
            for step_num, step_result in results['steps'].items():
                if step_result['tool'] == 'summarize' and step_result['success']:
                    final_summary = step_result['result'].get('summary')
                    break
            
            if final_summary:
                return final_summary
            
            # Fallback: create answer from available results
            answer_parts = []
            
            for step_num, step_result in results['steps'].items():
                if step_result['success']:
                    tool = step_result['tool']
                    result = step_result['result']
                    
                    if tool == 'search' and 'summary' in result:
                        answer_parts.append(f"📚 **Document Analysis**: {result['summary']}")
                    
                    elif tool == 'calculate' and 'calculations' in result:
                        calc_summary = ", ".join([f"{k}: {v}" for k, v in result['calculations'].items()])
                        if calc_summary:
                            answer_parts.append(f"🧮 **Calculations**: {calc_summary}")
                    
                    elif tool == 'analyze_trends' and 'summary' in result:
                        answer_parts.append(f"📈 **Trend Analysis**: {result['summary']}")
                    
                    elif tool == 'risk_assessment' and 'risk_assessment' in result:
                        risk_summary = ", ".join([f"{k}: {v}" for k, v in result['risk_assessment'].items()])
                        answer_parts.append(f"⚠️ **Risk Assessment**: {risk_summary}")
            
            if answer_parts:
                return "\n\n".join(answer_parts)
            else:
                return "I was unable to find sufficient information to answer your query. Please try rephrasing your question or uploading relevant documents."
                
        except Exception as e:
            return f"I encountered an error while synthesizing the answer: {str(e)}"
    
    def _calculate_confidence(self, results: Dict) -> float:
        """
        Calculate confidence score for the analysis
        """
        try:
            total_steps = len(results['steps'])
            successful_steps = sum(1 for step in results['steps'].values() if step['success'])
            
            if total_steps == 0:
                return 0.0
            
            base_confidence = successful_steps / total_steps
            
            # Adjust based on data quality
            data_quality_bonus = 0.0
            for step_result in results['steps'].values():
                if step_result['success'] and isinstance(step_result['result'], dict):
                    if 'documents' in step_result['result']:
                        docs = step_result['result']['documents']
                        if docs and len(docs) > 0:
                            avg_relevance = np.mean([doc.get('relevance', 0) for doc in docs])
                            data_quality_bonus += avg_relevance * 0.2
            
            return min(base_confidence + data_quality_bonus, 1.0)
            
        except Exception:
            return 0.5  # Default confidence
    
    def _extract_sources(self, results: Dict) -> List[str]:
        """
        Extract all sources used in the analysis
        """
        sources = set()
        
        for step_result in results['steps'].values():
            if step_result['success'] and isinstance(step_result['result'], dict):
                if 'documents' in step_result['result']:
                    for doc in step_result['result']['documents']:
                        if 'source' in doc:
                            sources.add(doc['source'])
                
                if 'sources_used' in step_result['result']:
                    sources.update(step_result['result']['sources_used'])
        
        return list(sources)
    
    # Helper methods for data extraction and analysis
    def _detect_content_type(self, content: str) -> str:
        """Detect the type of content (numerical, text, structured, etc.)"""
        if any(delimiter in content for delimiter in [',', '\t', '|']) and '\n' in content:
            return 'structured_data'
        elif re.search(r'\d+\.?\d*', content):
            return 'numerical'
        else:
            return 'text'
    
    def _extract_key_metrics(self, content: str) -> Dict[str, float]:
        """Extract numerical metrics from content"""
        metrics = {}
        
        # Look for common financial patterns
        patterns = {
            'revenue': r'revenue[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)',
            'profit': r'profit[:\s]+\$?(\d+(?:,\d{3})*(?:\.\d+)?)',
            'pe_ratio': r'p/e[:\s]+(\d+(?:\.\d+)?)',
            'price': r'price[:\s]+\$?(\d+(?:\.\d+)?)',
            'volume': r'volume[:\s]+(\d+(?:,\d{3})*)',
        }
        
        for metric, pattern in patterns.items():
            match = re.search(pattern, content.lower())
            if match:
                try:
                    value = float(match.group(1).replace(',', ''))
                    metrics[metric] = value
                except ValueError:
                    continue
        
        return metrics
    
    def _extract_numerical_data(self, accumulated_data: Dict) -> Dict[str, List]:
        """Extract numerical data from accumulated results"""
        numerical_data = {}
        
        for step_key, step_data in accumulated_data.items():
            if isinstance(step_data, dict) and 'documents' in step_data:
                for doc in step_data['documents']:
                    if 'key_metrics' in doc:
                        for metric, value in doc['key_metrics'].items():
                            if metric not in numerical_data:
                                numerical_data[metric] = []
                            numerical_data[metric].append(value)
        
        return numerical_data
    
    def _extract_time_series_data(self, accumulated_data: Dict) -> Dict[str, List]:
        """Extract time series data for trend analysis"""
        # Placeholder implementation
        return {}
    
    def _calculate_financial_ratios(self, data: Dict) -> Dict[str, float]:
        """Calculate financial ratios from available data"""
        ratios = {}
        
        # Example: if we have revenue and profit
        if 'revenue' in data and 'profit' in data:
            revenues = data['revenue']
            profits = data['profit']
            if revenues and profits:
                profit_margin = (np.mean(profits) / np.mean(revenues)) * 100
                ratios['profit_margin'] = profit_margin
        
        return ratios
    
    def _calculate_growth_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate growth metrics"""
        growth_metrics = {}
        
        for metric, values in data.items():
            if len(values) >= 2:
                growth_rate = ((values[-1] - values[0]) / values[0]) * 100
                growth_metrics[f'{metric}_growth'] = growth_rate
        
        return growth_metrics
    
    def _calculate_statistical_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate statistical metrics"""
        stats = {}
        
        for metric, values in data.items():
            if values:
                stats[f'{metric}_mean'] = np.mean(values)
                stats[f'{metric}_median'] = np.median(values)
                if len(values) > 1:
                    stats[f'{metric}_std'] = np.std(values)
        
        return stats
    
    def _calculate_return_metrics(self, data: Dict) -> Dict[str, float]:
        """Calculate return metrics"""
        return_metrics = {}
        
        if 'price' in data:
            prices = data['price']
            if len(prices) >= 2:
                total_return = ((prices[-1] - prices[0]) / prices[0]) * 100
                return_metrics['total_return'] = total_return
        
        return return_metrics
    
    def _generate_calculation_insights(self, calculations: Dict) -> List[str]:
        """Generate insights from calculations"""
        insights = []
        
        for metric, value in calculations.items():
            if 'growth' in metric and value > 0:
                insights.append(f"Positive growth detected in {metric.replace('_growth', '')}: {value:.2f}%")
            elif 'margin' in metric:
                if value > 20:
                    insights.append(f"Strong {metric}: {value:.2f}%")
                elif value > 10:
                    insights.append(f"Moderate {metric}: {value:.2f}%")
                else:
                    insights.append(f"Low {metric}: {value:.2f}%")
        
        return insights
    
    def _determine_trend_direction(self, data: List) -> str:
        """Determine trend direction"""
        if len(data) < 2:
            return 'insufficient_data'
        
        if data[-1] > data[0]:
            return 'upward'
        elif data[-1] < data[0]:
            return 'downward'
        else:
            return 'stable'
    
    def _calculate_volatility(self, data: List) -> float:
        """Calculate volatility"""
        if len(data) < 2:
            return 0.0
        return np.std(data) / np.mean(data) if np.mean(data) != 0 else 0.0
    
    def _calculate_recent_change(self, data: List) -> float:
        """Calculate recent change percentage"""
        if len(data) < 2:
            return 0.0
        return ((data[-1] - data[-2]) / data[-2]) * 100 if data[-2] != 0 else 0.0
    
    def _identify_pattern(self, data: List) -> str:
        """Identify patterns in data"""
        # Simplified pattern identification
        if len(data) < 3:
            return 'insufficient_data'
        
        # Check for consistent growth
        if all(data[i] <= data[i+1] for i in range(len(data)-1)):
            return 'consistent_growth'
        elif all(data[i] >= data[i+1] for i in range(len(data)-1)):
            return 'consistent_decline'
        else:
            return 'volatile'
    
    def _create_search_summary(self, results: List, query: str) -> str:
        """Create summary of search results"""
        if not results:
            return "No relevant documents found."
        
        high_relevance = [r for r in results if r['relevance'] > 0.7]
        
        if high_relevance:
            return f"Found {len(high_relevance)} highly relevant documents containing information about {query}."
        else:
            return f"Found {len(results)} potentially relevant documents."
    
    def _create_trend_summary(self, trends: Dict) -> str:
        """Create summary of trend analysis"""
        if not trends:
            return "No trend data available."
        
        upward_trends = [k for k, v in trends.items() if v.get('direction') == 'upward']
        downward_trends = [k for k, v in trends.items() if v.get('direction') == 'downward']
        
        summary_parts = []
        if upward_trends:
            summary_parts.append(f"Upward trends in: {', '.join(upward_trends)}")
        if downward_trends:
            summary_parts.append(f"Downward trends in: {', '.join(downward_trends)}")
        
        return '. '.join(summary_parts) if summary_parts else "Mixed trends observed."
    
    def _calculate_risk_metrics(self, data: Dict) -> Dict[str, str]:
        """Calculate risk metrics"""
        risk_metrics = {}
        
        for metric, values in data.items():
            if len(values) > 1:
                volatility = self._calculate_volatility(values)
                if volatility > 0.3:
                    risk_metrics[f'{metric}_risk'] = 'High'
                elif volatility > 0.1:
                    risk_metrics[f'{metric}_risk'] = 'Medium'
                else:
                    risk_metrics[f'{metric}_risk'] = 'Low'
        
        return risk_metrics
    
    def _generate_risk_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate risk recommendations"""
        recommendations = []
        
        high_risk_areas = [k for k, v in risk_assessment.items() if v == 'High']
        if high_risk_areas:
            recommendations.append(f"Monitor high-risk areas: {', '.join(high_risk_areas)}")
        
        recommendations.append("Diversify portfolio to reduce concentration risk")
        recommendations.append("Regular monitoring and rebalancing recommended")
        
        return recommendations
    
    def _extract_comparison_data(self, accumulated_data: Dict) -> Dict:
        """Extract data for comparison analysis"""
        # Placeholder implementation
        return {}
    
    def _create_comparison_summary(self, comparisons: Dict) -> str:
        """Create summary of comparison analysis"""
        if not comparisons:
            return "No comparison data available."
        
        summary_parts = []
        for metric, comp_data in comparisons.items():
            best = comp_data['best_performer']
            worst = comp_data['worst_performer']
            summary_parts.append(f"{metric}: {best} outperforms {worst}")
        
        return '. '.join(summary_parts)
