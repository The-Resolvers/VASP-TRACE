import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { TraceResult, NodeDetails } from '../../types/trace.types';
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

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .call(d3.zoom<SVGSVGElement, unknown>().on('zoom', (e) => {
        g.attr('transform', e.transform);
      }))
      .append('g');

    const g = svg.append('g');

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
        })
      );

    nodeGroup.append('circle')
      .attr('r', (d: any) => getNodeRadius(d))
      .attr('fill', (d: any) => getNodeColor(d))
      .attr('stroke', '#1e293b') // slate-800
      .attr('stroke-width', 2);

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
      .attr('font-family', 'monospace');

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
