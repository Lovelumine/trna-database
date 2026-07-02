import * as echarts from 'echarts/core';
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  VisualMapComponent
} from 'echarts/components';
import { BarChart, HeatmapChart, LineChart, TreemapChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';
import 'echarts-wordcloud';

echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  VisualMapComponent,
  BarChart,
  LineChart,
  TreemapChart,
  HeatmapChart,
  CanvasRenderer
]);

export { VChart };
