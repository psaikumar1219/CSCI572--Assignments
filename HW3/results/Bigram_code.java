import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.StringTokenizer;


public class WordCount {

  public static class Map extends Mapper<Object, Text, Text, Text> {

      private final Text bg = new Text();
      private final Text dId = new Text();

      @Override
      protected void map(Object key, Text value, Context context){
          String[] split = value.toString().split("\\t", 2);
          System.out.println("--------------------");
          System.out.println(split[0]);
          System.out.println("--------------------");
          dId.set(split[0]);

          String WS = split[1].replaceAll("[^a-zA-Z]+", " ").toLowerCase(Locale.ROOT);
          StringTokenizer tokenizer = new StringTokenizer(WS, " ");
          String fw = null;
          String sw = null;
          while (tokenizer.hasMoreTokens()) {
              String wordString = tokenizer.nextToken();
              if (!wordString.trim().isEmpty()) {
                  if (fw == null) {
                      fw = wordString;
                      continue;
                  } else if (sw == null) {
                      sw = wordString;
                  } else {
                      fw = sw;
                      sw = wordString;
                  }
                  bg.set(String.format("%s %s", fw, sw));

                  context.write(bg, dId);
              }
          }
      }
  }

  public static class Reduce extends Reducer<Text, Text, Text, Text> {

      @Override
      public void reduce(Text bg, Iterable<Text> dIds, Context context){
          Map<String, Integer> dIdToBFMap = new HashMap<>();
          for (Text dId : dIds) {
              String dIdString = dId.toString();
              dIdToBFMap.put(dIdString, dIdToBFMap.getOrDefault(dIdString, 0) + 1);
          }

          StringBuilder dIdBFs = new StringBuilder();
          for (Map.Entry<String, Integer> e : dIdToBFMap.entrySet()) {
              if (dIdBFs.length() > 0) {
                  dIdBFs.append("\t");
              }
              String dId = e.getKey();
              Integer BF = e.getValue();
              String dIdBF = String.format("%s:%d", dId, BF);
              System.out.println("--------------------");
              System.out.println(dIdBF);
              System.out.println("--------------------");
              dIdBFs.append(dIdBF);
          }

          context.write(bg, new Text(dIdBFs.toString()));
      }
  }
  

  public static void main(String[] args){
      String if = args[0];
      String of = args[1];

      System.out.println("--------------------");
      System.out.println(if);
      System.out.println("--------------------");
      System.out.println(of);
      System.out.println("--------------------");

      Configuration configuration = new Configuration();
      Job j = Job.getInstance(configuration, "Bigrams Inverted Index");
      j.setJarByClass(WordCount.class);
      j.setMapperClass(Map.class);
      j.setReducerClass(Reduce.class);
      j.setOutputKeyClass(Text.class);
      j.setOutputValueClass(Text.class);

      Path ifp = new Path(if);
      Path ofp = new Path(of);
      System.out.println("--------------------");
      System.out.println(ifp);
      System.out.println("--------------------");
      System.out.println(ofp);
      System.out.println("--------------------");
      FileSystem fs = ofp.getFileSystem(configuration);
      if (fs.exists(ofp)) {
          fs.delete(ofp, true);
      }
      FileInputFormat.addInputPath(j, ifp);
      FileOutputFormat.setOutputPath(j, ofp);

      System.exit(j.waitForCompletion(true) ? 0 : 1);
  }
}// WordCount

