#!/usr/bin/env python3
"""
Log Analysis Tool for Real-Time Monitoring Troubleshooting.

Analyzes real-time monitoring logs to identify detection issues.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from collections import defaultdict


class LogAnalyzer:
    """Analyzes real-time monitoring logs."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.chunks = []
        self.current_chunk = None
        
    def parse_logs(self):
        """Parse log file and extract chunk processing information."""
        
        with open(self.log_file, 'r') as f:
            for line in f:
                # Chunk processing start
                if 'Audio chunk: RMS=' in line:
                    if self.current_chunk:
                        self.chunks.append(self.current_chunk)
                    
                    # Extract timestamp
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
                    
                    # Extract RMS and Max
                    rms_match = re.search(r'RMS=([\d.]+)', line)
                    max_match = re.search(r'Max=([\d.]+)', line)
                    duration_match = re.search(r'Duration=([\d.]+)s', line)
                    
                    self.current_chunk = {
                        'timestamp': timestamp,
                        'rms': float(rms_match.group(1)) if rms_match else 0.0,
                        'max': float(max_match.group(1)) if max_match else 0.0,
                        'duration': float(duration_match.group(1)) if duration_match else 0.0,
                        'segments': [],
                        'skipped': False,
                        'no_speech': False,
                        'no_target': False,
                        'transcripts': []
                    }
                
                # Chunk skipped (too quiet)
                elif 'Chunk too quiet, skipping' in line and self.current_chunk:
                    self.current_chunk['skipped'] = True
                
                # No speech detected
                elif 'No speech segments detected in chunk' in line and self.current_chunk:
                    self.current_chunk['no_speech'] = True
                
                # Speech segments found
                elif 'Found' in line and 'speech segment(s) in chunk' in line and self.current_chunk:
                    seg_match = re.search(r'Found (\d+) speech segment', line)
                    if seg_match:
                        self.current_chunk['num_segments'] = int(seg_match.group(1))
                
                # Segment detection with similarity
                elif 'Segment [' in line and self.current_chunk:
                    # Extract segment info
                    segment_match = re.search(
                        r'Segment \[([\d.]+)s-([\d.]+)s\]: (TARGET|OTHER) \(similarity: ([\d.]+)\)',
                        line
                    )
                    if segment_match:
                        self.current_chunk['segments'].append({
                            'start': float(segment_match.group(1)),
                            'end': float(segment_match.group(2)),
                            'type': segment_match.group(3),
                            'similarity': float(segment_match.group(4))
                        })
                
                # No target detected
                elif 'No target speaker detected in chunk' in line and self.current_chunk:
                    self.current_chunk['no_target'] = True
                
                # Target detected
                elif 'Target speaker detected in' in line and self.current_chunk:
                    target_match = re.search(r'detected in (\d+) segment', line)
                    if target_match:
                        self.current_chunk['target_segments'] = int(target_match.group(1))
                
                # Transcript
                elif 'Real-time transcript:' in line and self.current_chunk:
                    text_match = re.search(r'\[([\d.]+)s\] (.+)', line)
                    if text_match:
                        self.current_chunk['transcripts'].append({
                            'time': float(text_match.group(1)),
                            'text': text_match.group(2)
                        })
        
        # Add last chunk
        if self.current_chunk:
            self.chunks.append(self.current_chunk)
    
    def analyze(self):
        """Analyze parsed chunks and generate report."""
        
        if not self.chunks:
            print("❌ No chunks found in log file!")
            return
        
        print("\n" + "="*80)
        print("REAL-TIME MONITORING LOG ANALYSIS")
        print("="*80)
        
        # Overall statistics
        total_chunks = len(self.chunks)
        skipped_chunks = sum(1 for c in self.chunks if c.get('skipped'))
        no_speech_chunks = sum(1 for c in self.chunks if c.get('no_speech'))
        no_target_chunks = sum(1 for c in self.chunks if c.get('no_target'))
        target_detected_chunks = sum(1 for c in self.chunks if c.get('target_segments', 0) > 0)
        transcribed_chunks = sum(1 for c in self.chunks if c.get('transcripts'))
        
        print(f"\n📊 OVERALL STATISTICS")
        print(f"  Total chunks processed: {total_chunks}")
        print(f"  Skipped (too quiet): {skipped_chunks} ({skipped_chunks/total_chunks*100:.1f}%)")
        print(f"  No speech detected: {no_speech_chunks} ({no_speech_chunks/total_chunks*100:.1f}%)")
        print(f"  Speech but no target: {no_target_chunks} ({no_target_chunks/total_chunks*100:.1f}%)")
        print(f"  Target detected: {target_detected_chunks} ({target_detected_chunks/total_chunks*100:.1f}%)")
        print(f"  Transcribed: {transcribed_chunks} ({transcribed_chunks/total_chunks*100:.1f}%)")
        
        # Audio level analysis
        print(f"\n🔊 AUDIO LEVELS")
        rms_values = [c['rms'] for c in self.chunks if not c.get('skipped')]
        if rms_values:
            print(f"  RMS - Min: {min(rms_values):.4f}, Max: {max(rms_values):.4f}, Avg: {sum(rms_values)/len(rms_values):.4f}")
        
        # Similarity analysis
        print(f"\n🎯 SIMILARITY SCORES")
        target_similarities = []
        other_similarities = []
        
        for chunk in self.chunks:
            for seg in chunk.get('segments', []):
                if seg['type'] == 'TARGET':
                    target_similarities.append(seg['similarity'])
                else:
                    other_similarities.append(seg['similarity'])
        
        if target_similarities:
            print(f"  TARGET segments:")
            print(f"    Count: {len(target_similarities)}")
            print(f"    Min: {min(target_similarities):.3f}")
            print(f"    Max: {max(target_similarities):.3f}")
            print(f"    Avg: {sum(target_similarities)/len(target_similarities):.3f}")
        else:
            print(f"  ❌ No TARGET segments detected!")
        
        if other_similarities:
            print(f"  OTHER segments:")
            print(f"    Count: {len(other_similarities)}")
            print(f"    Min: {min(other_similarities):.3f}")
            print(f"    Max: {max(other_similarities):.3f}")
            print(f"    Avg: {sum(other_similarities)/len(other_similarities):.3f}")
        
        # Identify problem chunks (speech detected but target missed)
        print(f"\n⚠️  PROBLEM CHUNKS (Speech detected but target missed)")
        problem_chunks = [
            c for c in self.chunks 
            if c.get('segments') and not c.get('target_segments', 0) > 0
        ]
        
        if problem_chunks:
            print(f"  Found {len(problem_chunks)} problem chunks:")
            for i, chunk in enumerate(problem_chunks[:10]):  # Show first 10
                print(f"\n  Chunk #{i+1} at {chunk['timestamp']}")
                print(f"    RMS: {chunk['rms']:.4f}, Max: {chunk['max']:.4f}")
                print(f"    Segments detected: {len(chunk['segments'])}")
                for seg in chunk['segments']:
                    print(f"      [{seg['start']:.1f}s-{seg['end']:.1f}s] {seg['type']} (similarity: {seg['similarity']:.3f})")
            
            if len(problem_chunks) > 10:
                print(f"\n  ... and {len(problem_chunks) - 10} more problem chunks")
        else:
            print(f"  ✅ No problem chunks found!")
        
        # Transcription timeline
        print(f"\n📝 TRANSCRIPTION TIMELINE")
        transcripts_found = False
        for chunk in self.chunks:
            if chunk.get('transcripts'):
                transcripts_found = True
                for t in chunk['transcripts']:
                    print(f"  [{chunk['timestamp']}] {t['text'][:60]}...")
        
        if not transcripts_found:
            print(f"  ❌ No transcripts found!")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        
        if not target_similarities:
            print(f"  🔴 CRITICAL: No target speaker detected at all!")
            print(f"     → Check if correct profile is selected")
            print(f"     → Verify profile quality is good")
            print(f"     → Try re-creating the profile with better audio")
        
        elif target_similarities and max(target_similarities) < 0.75:
            print(f"  🟡 WARNING: Low similarity scores (max: {max(target_similarities):.3f})")
            print(f"     → Current threshold: 0.75")
            print(f"     → Consider lowering threshold to {max(target_similarities) * 0.9:.2f}")
            print(f"     → Or re-record profile in similar acoustic conditions")
        
        if other_similarities and max(other_similarities) > 0.70:
            print(f"  🟡 WARNING: Other speakers have high similarity (max: {max(other_similarities):.3f})")
            print(f"     → Risk of false positives")
            print(f"     → Consider raising threshold slightly")
        
        if problem_chunks:
            avg_problem_rms = sum(c['rms'] for c in problem_chunks) / len(problem_chunks)
            print(f"  🟡 INFO: {len(problem_chunks)} chunks had speech but missed target")
            print(f"     → Average RMS: {avg_problem_rms:.4f}")
            print(f"     → Check if speaking too quietly or at wrong distance from mic")
        
        print("\n" + "="*80)


def main():
    """Main function."""
    
    # Default log file
    log_file = Path("logs/realtime_debug.log")
    
    # Check if log file specified as argument
    if len(sys.argv) > 1:
        log_file = Path(sys.argv[1])
    
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        print(f"\nUsage: python analyze_logs.py [log_file]")
        print(f"Default: {log_file}")
        sys.exit(1)
    
    print(f"📂 Analyzing log file: {log_file}")
    print(f"📏 File size: {log_file.stat().st_size / 1024:.1f} KB")
    
    # Parse and analyze
    analyzer = LogAnalyzer(log_file)
    analyzer.parse_logs()
    analyzer.analyze()


if __name__ == "__main__":
    main()
