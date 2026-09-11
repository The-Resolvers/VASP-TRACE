import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { TraceResult } from '../../types/trace.types';
import { getD3Config, getNodeColor, getNodeRadius } from '../../utils/d3Config';

interface GraphVisualizerProps {
  data: TraceResult;
}

export const GraphVisualizer: React.FC<GraphVisualizerProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !wrapperRef.current || !data) return;

    const width = wrapperRef.current.clientWidth;
    const height = wrapperRef.current.clientHeight;
    
    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    // 1. Setup the SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // 2. Create the inner group 'g'
    const g = svg.append('g');

    // 3. Attach the zoom handler to 'svg' and apply the transform to 'g'
    svg.call(d3.zoom<SVGSVGElement, unknown>().on('zoom', (e) => {
        g.attr('transform', e.transform);
    }));

    const config = getD3Config(width, height);

    // Setup simulation
    const simulation = d3.forceSimulation(data.nodes as d3.SimulationNodeDatum[])
      .force('link', d3.forceLink(data.links).id((d: any) => d.id).distance(config.linkDistance))
      .force('charge', d3.forceManyBody().strength(config.chargeStrength))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius((d: any) => getNodeRadius(d) + 10));

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', '#475569') // slate-600
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6);

    // Draw nodes
    const nodeGroup = g.append('g')
      .selectAll('g')
      .data(data.nodes)
      .join('g')
      .call(d3.drag<SVGGElement, any>()
        .on('start', (e, d) => {
          if (!e.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (e, d) => {
          d.fx = e.x;
          d.fy = e.y;
        })
        .on('end', (e, d) => {
          if (!e.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }) as any
      );

    nodeGroup.append('circle')
      .attr('r', (d: any) => getNodeRadius(d))
      .attr('fill', (d: any) => getNodeColor(d))
      .attr('stroke', '#1e293b') // slate-800
      .attr('stroke-width', 2);

    nodeGroup.append('title')
      .text((d: any) => d.id);

    nodeGroup.append('text')
      .text((d: any) => {
        if (d.is_source) return 'Source';
        if (d.is_exchange) return d.vasp_name || 'VASP';
        if (d.is_mixer) return 'Mixer';
        return d.id.substring(0, 6) + '...';
      })
      .attr('x', 12)
      .attr('y', 4)
      .attr('fill', '#cbd5e1') // slate-300
      .attr('font-size', '10px')
      .attr('font-family', 'monospace')
      .style('cursor', 'pointer')
      .on('click', function(e, d: any) {
        const el = d3.select(this);
        const parent = d3.select(this.parentNode as any);
        const copyBtn = parent.select('.copy-btn');
        const currentText = el.text();
        
        // Toggle logic
        if (currentText === d.id) {
          // Revert to short name
          if (d.is_source) el.text('Source');
          else if (d.is_exchange) el.text(d.vasp_name || 'VASP');
          else if (d.is_mixer) el.text('Mixer');
          else el.text(d.id.substring(0, 6) + '...');
          
          copyBtn.style('display', 'none');
        } else {
          // Expand to full Bitcoin Address
          el.text(d.id);
          copyBtn.style('display', 'block');
        }
      });

    // Lucide Icons SVG strings (paths only, no nested <svg> tags which break inside <g>)
    const COPY_SVG = `<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>`;
    const CHECK_SVG = `<path d="M20 6 9 17l-5-5"/>`;

    // Clipboard icon (hidden by default)
    nodeGroup.append('g')
      .attr('class', 'copy-btn')
      // translate positions the icon after the text, scale(0.5) shrinks it from 24x24 to 12x12
      .attr('transform', (d: any) => `translate(${18 + (d.id.length * 6)}, -4) scale(0.5)`)
      .style('cursor', 'pointer')
      .style('display', 'none')
      .attr('fill', 'none')
      .attr('stroke', '#94a3b8') // slate-400
      .attr('stroke-width', '2')
      .attr('stroke-linecap', 'round')
      .attr('stroke-linejoin', 'round')
      .html(COPY_SVG)
      .on('click', function(e, d: any) {
         e.stopPropagation(); // Prevent the node drag/click from firing
         
         // Robust clipboard copy with fallback
         if (navigator.clipboard && window.isSecureContext) {
             navigator.clipboard.writeText(d.id);
         } else {
             const textArea = document.createElement("textarea");
             textArea.value = d.id;
             document.body.appendChild(textArea);
             textArea.focus();
             textArea.select();
             try { document.execCommand('copy'); } catch (err) {}
             document.body.removeChild(textArea);
         }
         
         const btn = d3.select(this);
         btn.attr('stroke', '#4ade80') // green-400
            .html(CHECK_SVG);
         setTimeout(() => {
            btn.attr('stroke', '#94a3b8')
               .html(COPY_SVG);
         }, 1500);
      });

    // Simulation tick updates
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      nodeGroup.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [data]);

  return (
    <div ref={wrapperRef} className="w-full h-full min-h-[600px] bg-slate-900 rounded-lg overflow-hidden border border-slate-700">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
};
