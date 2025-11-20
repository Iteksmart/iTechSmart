import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@mui/material';
import { Alert, AlertTitle } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import { ZoomIn, ZoomOut, CenterFocusStrong, Download, Refresh } from '@mui/icons-material';
import {
  Box,
  Button,
  ButtonGroup,
  Chip,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Slider,
  Stack,
  TextField,
  Typography,
  useTheme,
} from '@mui/material';

interface GraphNode {
  id: string;
  label: string;
  type: 'service' | 'product' | 'dependency' | 'metric' | 'alert';
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  data: {
    version?: string;
    status?: 'healthy' | 'warning' | 'error';
    description?: string;
    metrics?: Record<string, number>;
    relationships?: string[];
  };
}

interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: 'dependency' | 'communication' | 'data_flow' | 'impact';
  strength?: number;
  data?: {
    frequency?: number;
    volume?: number;
    latency?: number;
  };
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface KnowledgeGraphVisualizationProps {
  data: GraphData;
  onNodeClick?: (node: GraphNode) => void;
  onLinkClick?: (link: GraphLink) => void;
  onGraphUpdate?: (data: GraphData) => void;
  height?: number;
  width?: number;
}

const KnowledgeGraphVisualization: React.FC<KnowledgeGraphVisualizationProps> = ({
  data,
  onNodeClick,
  onLinkClick,
  onGraphUpdate,
  height = 600,
  width = 1200,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedLink, setSelectedLink] = useState<GraphLink | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [linkStrength, setLinkStrength] = useState<number>(50);
  const [isSimulating, setIsSimulating] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [zoom, setZoom] = useState<number>(1);
  const theme = useTheme();

  // Color schemes for different node types
  const getNodeColor = useCallback((node: GraphNode): string => {
    switch (node.type) {
      case 'service':
        return node.data.status === 'healthy' ? '#4CAF50' : 
               node.data.status === 'warning' ? '#FF9800' : '#F44336';
      case 'product':
        return '#2196F3';
      case 'dependency':
        return '#9C27B0';
      case 'metric':
        return '#FFC107';
      case 'alert':
        return '#FF5722';
      default:
        return '#607D8B';
    }
  }, []);

  // Get link color based on type and strength
  const getLinkColor = useCallback((link: GraphLink): string => {
    const opacity = link.strength ? link.strength / 100 : 0.6;
    switch (link.type) {
      case 'dependency':
        return `rgba(33, 150, 243, ${opacity})`;
      case 'communication':
        return `rgba(76, 175, 80, ${opacity})`;
      case 'data_flow':
        return `rgba(255, 152, 0, ${opacity})`;
      case 'impact':
        return `rgba(244, 67, 54, ${opacity})`;
      default:
        return `rgba(96, 125, 139, ${opacity})`;
    }
  }, []);

  // Filter data based on search and filter criteria
  const getFilteredData = useCallback((): GraphData => {
    let filteredNodes = [...data.nodes];
    let filteredLinks = [...data.links];

    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filteredNodes = filteredNodes.filter(node =>
        node.label.toLowerCase().includes(searchLower) ||
        node.data.description?.toLowerCase().includes(searchLower)
      );
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      filteredLinks = filteredLinks.filter(link =>
        typeof link.source === 'string' ? nodeIds.has(link.source) : nodeIds.has(link.source.id)
      ) && typeof link.target === 'string' ? nodeIds.has(link.target) : nodeIds.has(link.target.id);
    }

    // Apply type filter
    if (filter !== 'all') {
      filteredNodes = filteredNodes.filter(node => node.type === filter);
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      filteredLinks = filteredLinks.filter(link =>
        typeof link.source === 'string' ? nodeIds.has(link.source) : nodeIds.has(link.source.id)
      ) && typeof link.target === 'string' ? nodeIds.has(link.target) : nodeIds.has(link.target.id);
    }

    return { nodes: filteredNodes, links: filteredLinks };
  }, [data, searchTerm, filter]);

  // Handle node selection
  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    setSelectedLink(null);
    onNodeClick?.(node);
  }, [onNodeClick]);

  // Handle link selection
  const handleLinkClick = useCallback((link: GraphLink) => {
    setSelectedLink(link);
    setSelectedNode(null);
    onLinkClick?.(link);
  }, [onLinkClick]);

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev + 0.2, 3));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev - 0.2, 0.5));
  }, []);

  const handleZoomReset = useCallback(() => {
    setZoom(1);
  }, []);

  // Export graph data
  const handleExport = useCallback(() => {
    const exportData = {
      nodes: data.nodes.map(node => ({
        id: node.id,
        label: node.label,
        type: node.type,
        data: node.data,
      })),
      links: data.links.map(link => ({
        source: typeof link.source === 'string' ? link.source : link.source.id,
        target: typeof link.target === 'string' ? link.target : link.target.id,
        type: link.type,
        strength: link.strength,
        data: link.data,
      })),
      metadata: {
        exportTime: new Date().toISOString(),
        version: '1.6.0',
        totalNodes: data.nodes.length,
        totalLinks: data.links.length,
      },
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `knowledge-graph-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [data]);

  // Refresh graph data
  const handleRefresh = useCallback(async () => {
    setLoading(true);
    try {
      // Simulate API call to refresh data
      await new Promise(resolve => setTimeout(resolve, 1000));
      onGraphUpdate?.(data);
    } finally {
      setLoading(false);
    }
  }, [data, onGraphUpdate]);

  const filteredData = getFilteredData();

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardHeader
        title={
          <Stack direction="row" alignItems="center" spacing={2}>
            <Typography variant="h6">Knowledge Graph Visualization</Typography>
            <Chip
              label={`${filteredData.nodes.length} nodes, ${filteredData.links.length} links`}
              size="small"
              color="primary"
            />
          </Stack>
        }
        action={
          <Stack direction="row" spacing={1}>
            <LoadingButton
              loading={loading}
              onClick={handleRefresh}
              startIcon={<Refresh />}
              size="small"
            >
              Refresh
            </LoadingButton>
            <Button
              onClick={handleExport}
              startIcon={<Download />}
              size="small"
              variant="outlined"
            >
              Export
            </Button>
          </Stack>
        }
      />
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* Controls */}
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
          <TextField
            size="small"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ minWidth: 200 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Filter by Type</InputLabel>
            <Select
              value={filter}
              label="Filter by Type"
              onChange={(e) => setFilter(e.target.value)}
            >
              <MenuItem value="all">All Types</MenuItem>
              <MenuItem value="service">Services</MenuItem>
              <MenuItem value="product">Products</MenuItem>
              <MenuItem value="dependency">Dependencies</MenuItem>
              <MenuItem value="metric">Metrics</MenuItem>
              <MenuItem value="alert">Alerts</MenuItem>
            </Select>
          </FormControl>

          <Box sx={{ minWidth: 200, maxWidth: 300 }}>
            <Typography variant="caption" display="block" gutterBottom>
              Link Strength: {linkStrength}%
            </Typography>
            <Slider
              value={linkStrength}
              onChange={(_, value) => setLinkStrength(value as number)}
              min={10}
              max={100}
              size="small"
            />
          </Box>

          <ButtonGroup size="small">
            <Button onClick={handleZoomIn}>
              <ZoomIn />
            </Button>
            <Button onClick={handleZoomOut}>
              <ZoomOut />
            </Button>
            <Button onClick={handleZoomReset}>
              <CenterFocusStrong />
            </Button>
          </ButtonGroup>
        </Stack>

        {/* Graph Visualization */}
        <Box sx={{ flex: 1, border: 1, borderColor: 'divider', borderRadius: 1, overflow: 'hidden' }}>
          <svg
            ref={svgRef}
            width={width}
            height={height}
            style={{ width: '100%', height: '100%' }}
            viewBox={`0 0 ${width} ${height}`}
          >
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon
                  points="0 0, 10 3.5, 0 7"
                  fill="#999"
                />
              </marker>
            </defs>

            <g transform={`scale(${zoom})`}>
              {/* Links */}
              {filteredData.links.map((link, index) => {
                const source = typeof link.source === 'string' 
                  ? filteredData.nodes.find(n => n.id === link.source)
                  : link.source;
                const target = typeof link.target === 'string'
                  ? filteredData.nodes.find(n => n.id === link.target)
                  : link.target;
                
                if (!source || !target) return null;

                const isSelected = selectedLink === link;
                const strokeWidth = isSelected ? 3 : Math.max(1, (link.strength || 50) / 25);

                return (
                  <g key={`link-${index}`}>
                    <line
                      x1={source.x || 0}
                      y1={source.y || 0}
                      x2={target.x || 0}
                      y2={target.y || 0}
                      stroke={getLinkColor(link)}
                      strokeWidth={strokeWidth}
                      markerEnd="url(#arrowhead)"
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleLinkClick(link)}
                      opacity={isSelected ? 1 : 0.6}
                    />
                    {link.data?.volume && (
                      <text
                        x={(source.x + target.x) / 2}
                        y={(source.y + target.y) / 2}
                        fontSize="10"
                        fill="#666"
                        textAnchor="middle"
                      >
                        {link.data.volume}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Nodes */}
              {filteredData.nodes.map((node) => {
                const isSelected = selectedNode === node;
                const nodeRadius = isSelected ? 12 : 8;

                return (
                  <g key={`node-${node.id}`} transform={`translate(${node.x || 0}, ${node.y || 0})`}>
                    <circle
                      r={nodeRadius}
                      fill={getNodeColor(node)}
                      stroke={isSelected ? theme.palette.primary.main : '#fff'}
                      strokeWidth={isSelected ? 3 : 2}
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleNodeClick(node)}
                    />
                    <text
                      y={nodeRadius + 15}
                      fontSize="12"
                      fill="#333"
                      textAnchor="middle"
                      style={{ pointerEvents: 'none' }}
                    >
                      {node.label}
                    </text>
                    {node.data.status && (
                      <circle
                        cy={-nodeRadius - 5}
                        r={3}
                        fill={node.data.status === 'healthy' ? '#4CAF50' :
                             node.data.status === 'warning' ? '#FF9800' : '#F44336'}
                      />
                    )}
                  </g>
                );
              })}
            </g>
          </svg>
        </Box>

        {/* Selection Details */}
        {selectedNode && (
          <Alert severity="info">
            <AlertTitle>Selected Node: {selectedNode.label}</AlertTitle>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <Typography variant="body2">
                Type: <strong>{selectedNode.type}</strong>
              </Typography>
              {selectedNode.data.version && (
                <Typography variant="body2">
                  Version: <strong>{selectedNode.data.version}</strong>
                </Typography>
              )}
              {selectedNode.data.status && (
                <Typography variant="body2">
                  Status: <strong>{selectedNode.data.status}</strong>
                </Typography>
              )}
              {selectedNode.data.description && (
                <Typography variant="body2" sx={{ flex: 1, minWidth: 200 }}>
                  {selectedNode.data.description}
                </Typography>
              )}
            </Stack>
          </Alert>
        )}

        {selectedLink && (
          <Alert severity="warning">
            <AlertTitle>Selected Link</AlertTitle>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <Typography variant="body2">
                Type: <strong>{selectedLink.type}</strong>
              </Typography>
              {selectedLink.strength && (
                <Typography variant="body2">
                  Strength: <strong>{selectedLink.strength}%</strong>
                </Typography>
              )}
              {selectedLink.data?.frequency && (
                <Typography variant="body2">
                  Frequency: <strong>{selectedLink.data.frequency}/min</strong>
                </Typography>
              )}
              {selectedLink.data?.latency && (
                <Typography variant="body2">
                  Latency: <strong>{selectedLink.data.latency}ms</strong>
                </Typography>
              )}
            </Stack>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default KnowledgeGraphVisualization;